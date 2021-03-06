#!/usr/bin/env python
# coding=utf-8

from fc_prediction import Prediciton
from mlog import MLog
from instrument import Instrument
from order import Order, CombOffset, OrderPrice, Direction, OrderStatus
from account import Account
from daily_record import DailyRecord,SummaryRecord
import numpy as np
from collections import OrderedDict
import time,datetime
import pandas as pd

DEFAULT_AMOUNT = 1
DEFAULT_CASH = 1000000
#沪白银手续费 万分之0.5  保证金 合约价值的7% 最小1元/千克  最小单位: 15千克/手

class Strange(object):
    __strategy_id = 1001
    __account_id = 10001
    
    
    def __init__(self, limit_order):
        
        
        self.__bar_list = []


        self.__pred = Prediciton()
        self.__pred.init_model(1,'../test/model/')
        self.__limit_order = OrderedDict() # 委托单队列
        self.long_volumes = OrderedDict() #当前多头持仓情况
        self.short_volumes = OrderedDict() #当前空头持仓情况

        # 当日行情结束后，进行导出，用于分析

        self.__history_limit_order = OrderedDict() # 历史委托单
        self.__history_limit_volumes = OrderedDict() # 历史成交记录

        self.__working_limit_order = limit_order



        # 交易记录存储
        self.__trader_record = OrderedDict()
        
        
        # 暂时将账户和合约初始化放在策略内初始化

        # 账户初始化
        self.__account = Account()
        self.__account.set_account_id(self.__account_id)
        self.__account.set_init_cash(DEFAULT_CASH)

        #期货合约初始化 
        self.__instrument = Instrument()
        self.__instrument.set_fee(0.00005)
        self.__instrument.set_short_margin_ratio(0.07)
        self.__instrument.set_long_margin_ratio(0.07)
        self.__instrument.set_price_tick(1)
        self.__instrument.set_min_limit_order_volume(15)
        self.__instrument.set_instrument_id('ag')
        self.__instrument.set_instrument_name('白银')



    def __reset(self):
        self.__limit_order.clear()
        self.__history_limit_order.clear()
        self.__history_limit_order.clear()
        self.__working_limit_order.clear()

    def record(self):
        self.__account.dump()
        record = DailyRecord()
        record.set_close_profit(self.__account.close_profit())
        record.set_position_profit(self.__account.position_profit())
        record.set_commssion(self.__account.commission())
        record.set_limit_volume(self.__history_limit_volumes)
        record.set_limit_order(self.__history_limit_order)
        
        
        record.set_mktime(self.__bar_list[-1].mktime())

        MLog.write().info('mkdate:%d, available_cash:%f,profit:%f'%(record.mktime(),self.__account.available_cash(), record.all_profit()))
        self.__trader_record[record.mktime()] = record
        self.__account.reset()
        self.__reset()

    def calc_result(self):
        max_profit = 0.0
        total_profit = 0.0
        base_value = 0.0
        for key,value in self.__trader_record.items():
            total_profit += value.all_profit()

        starting_cash = self.__account.starting_cash()
        base_value = (int(abs(total_profit) / starting_cash) + 1) * self.__account.starting_cash()
        MLog.write().info('all:%f, base_value:%f',total_profit,base_value)
        total_profit = 0.0

        df = pd.DataFrame(columns = ['mktime','interests','value','retrace','chg','log_chg','profit'])
        # 计算每日权益，每日净值, 涨跌幅，回撤，日对数收益
        last_value = 0.0
        for mktime,daily_record in self.__trader_record.items():
            daily_record.set_base_value(base_value)
            daily_record.set_last_value(last_value)
            daily_record.set_max_profit(max_profit)
            daily_record.set_last_profit(total_profit)
            daily_record.calc_result()
            daily_record.dump()
            df = df.append(pd.DataFrame({'mktime':mktime, 'interests':daily_record.interests(),
                                         'value':daily_record.value(), 'retrace': daily_record.retrace(),
                                         'chg':daily_record.chg(),'log_chg':daily_record.log_chg(),
                                         'profit':daily_record.all_profit()},index=['mktime']), ignore_index=True)

            total_profit += daily_record.all_profit()
            if max_profit < total_profit:
                max_profit = total_profit
            last_value = daily_record.value()
            base_value += daily_record.all_profit()
            
        chg_mean = np.mean(df['log_chg'])
        chg_std = np.std(df['log_chg'])

        summary_record = SummaryRecord()
        summary_record.set_chg_mean(chg_mean)
        summary_record.set_chg_std(chg_std)
        summary_record.set_trade_count(df.shape[0])
        summary_record.set_final_value(df['value'].values[-1])
        summary_record.set_max_retr(np.min(df['retrace']))


        summary_record.calc_record(df[df['chg'] > 0.00].shape[0])
        summary_record.dump()
        df.to_csv('result_strange.csv', encoding = 'utf-8')


    def save(self):
        '''
        filename = 'strange' + '.csv'
        fieldnames = ['mktime','interests','value','retrace','chg','log_chg','profit',]
        with open(filename, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for mktime,daily_record in self.__trader_record.items():
                writer.writerow({'mktime':mktime,'interests':daily_record.interests(),'value':daily_record.value(),'retrace':daily_record.retrace(),
                                 'chg':daily_record.chg(),'log_chg':daily_record.log_chg(),'profit':daily_record.all_profit()})
        '''


    # close, high, low open  下一分钟收盘价  
    def __on_fc_single(self):
        for bar in self.__bar_list:
            if self.__bar_list.index(bar) == 0:
                x = np.array([bar.close_price(), bar.high_price(), bar.low_price(), bar.open_price(),bar.volume(),
                             bar.last_buy_price(),bar.last_buy_vol(),bar.last_sell_price(),bar.last_sell_vol()])
            else:
                t = np.array([bar.close_price(), bar.high_price(), bar.low_price(), bar.open_price(),bar.volume(),
                             bar.last_buy_price(),bar.last_buy_vol(),bar.last_sell_price(),bar.last_sell_vol()])
                x = np.vstack((x,t))

        close_price = self.__pred.new_signal(x)
        return close_price
        # pred = Prediciton()
        # price = pred.signal(x)
        # return  price
        # rand =  int(np.std(x) * 1000  % 2)
        # if rand == 0:
        #    return np.mean(x) + np.std(x)
        # else:
        #    return np.mean(x)


    # 多头成本控制
    def __is_long_order(self, order_price, close_price, next_price):
        long_fee = (order_price * self.__instrument.min_limit_order_volume() * self.__instrument.fee()) * 2  # 多头建仓手续费
        long_profit = abs(order_price - next_price) * self.__instrument.min_limit_order_volume() # 多头最小利润
        
        if long_profit > long_fee:
            MLog.write().debug('long_profit:%f more than long_fee:%f allow open long'%(long_profit, long_fee))
        else:
            MLog.write().debug('long_profit:%f less than long_fee:%f not open long'%(long_profit, long_fee))
        return 1 if long_profit > long_fee else 0
    
    # 空头成本控制
    def __is_short_order(self, order_price, close_price, next_price):
        short_fee = (order_price * self.__instrument.min_limit_order_volume() * self.__instrument.fee()) * 2
        short_profit = abs(order_price - next_price) * self.__instrument.min_limit_order_volume() # 空头最小利润
        
        if short_profit > short_fee:
            MLog.write().debug('short_profit:%f more than short_fee:%f allow  open short'%(short_profit, short_fee))
        else:
            MLog.write().debug('short_profit:%f less than short_fee:%f not open short'%(short_profit, short_fee))
        return 1 if short_profit > short_fee else 0

    def cancel_order(self):
        for oid, order in self.__limit_order.items():
            del self.__working_limit_order[oid]
            del self.__limit_order[oid]
            order.set_status(OrderStatus.cacelled)
            self.__history_limit_order[oid] = order
            self.__account.canncel_order_cash(order.margin(), order.fee())
    
    
    # 多头操作
    def __long_operation(self, next_price, last_bar, amount):
        self.cancel_order()
        #是否持有多头仓
        if len(self.long_volumes) == 0:
            if self.__is_long_order(last_bar.last_sell_price(), last_bar.close_price(), next_price) == 1:
                order = self.__long_open(last_bar.last_sell_price(), amount,last_bar.current_time())
                order.dump()
                self.__account.insert_order_cash(order.margin(), order.fee())
                self.__working_limit_order[order.order_id()] = order
                self.__limit_order[order.order_id()] = order
                self.__account.dump()
        else: # 已经持有多头仓
            for k,v in self.long_volumes.items():
                MLog.write().debug("hold long volumens:%d price:%f close_price:%f" %(v.amount(),v.limit_price(), last_bar.close_price()))
        #是否有空头仓
        if len(self.short_volumes) > 0:
            MLog.write().debug("long singal start close short volume")
            for k,v in self.short_volumes.items():
                order = self.__short_close(last_bar.last_sell_price(), v.amount(),last_bar.current_time())
                order.set_hold_volume_id(v.trader_id())
                self.__account.insert_order_cash(order.margin(), order.fee())
                self.__working_limit_order[order.order_id()] = order
                self.__limit_order[order.order_id()] = order
                order.dump()
                self.__account.dump()

   # 空头操作
    def __short_operation(self, next_price, last_bar, amount):
        self.cancel_order()
        # 是否持有空头仓
        if len(self.short_volumes) == 0:
            if self.__is_short_order(last_bar.last_buy_price(), last_bar.close_price(), next_price) == 1:
                order = self.__short_open(last_bar.last_buy_price(), amount, last_bar.current_time())
                order.dump()
                self.__account.insert_order_cash(order.margin(), order.fee())
                self.__working_limit_order[order.order_id()] = order
                self.__limit_order[order.order_id()] = order
                self.__account.dump()
        else:
            for k,v in self.short_volumes.items():
                MLog.write().debug("hold short volumens:%d price:%f close_price:%f" %(v.amount(),v.limit_price(),last_bar.close_price()))
        # 是否持有多头仓
        if len(self.long_volumes) > 0: 
            MLog.write().debug("short singal start close long volume")
            for k,v in self.long_volumes.items():
                order = self.__long_close(last_bar.last_buy_price(), v.amount(), last_bar.current_time())
                order.set_hold_volume_id(v.trader_id())
                self.__account.insert_order_cash(order.margin(), order.fee())
                self.__working_limit_order[order.order_id()] = order
                self.__limit_order[order.order_id()] = order
                order.dump()
                self.__account.dump()
    # 多头开仓
    def __long_open(self, order_price, amount, bar_time):
        return self.__create_limit_price(order_price, amount, CombOffset.open, Direction.buy_direction,bar_time)

    # 多头平仓
    def __long_close(self, order_price, amount, bar_time):
        return self.__create_limit_price(order_price, amount, CombOffset.close, Direction.sell_direction,bar_time)
    
    # 空头开仓
    def __short_open(self, order_price, amount, bar_time):
        return self.__create_limit_price(order_price, amount, CombOffset.open, Direction.sell_direction,bar_time)

    # 空头平仓
    def __short_close(self, order_price, amount, bar_time):
        return self.__create_limit_price(order_price, amount, CombOffset.close, Direction.buy_direction,bar_time)

    # 创建限价单
    def __create_limit_price(self, order_price, amount, off_flag, direction,bar_time):
        # pdb.set_trace()
        order = Order()
        order.create_order_id()
        order.set_create_time(bar_time)
        order.set_account_id(self.__account_id)
        order.set_symbol(self.__instrument.instrument_id())
        order.set_comb_offset_flag(off_flag)
        order.set_order_price_type(OrderPrice.limit_price)
        order.set_limit_price(order_price)
        order.set_direction(direction)
        order.set_amount(amount)
        order.set_strategy_id(self.__strategy_id)
        order.set_min_volume(self.__instrument.min_limit_order_volume())
        if direction == Direction.buy_direction:
            order.set_margin(self.__instrument.long_margin_ratio())
        else:
            order.set_margin(self.__instrument.short_margin_ratio())

        order.set_fee(self.__instrument.fee())
        return order


    def on_volume(self, vol, order):
        # 从委托队列中删除
        # pdb.set_trace()
        del self.__limit_order[vol.order_id()]
        self.__history_limit_volumes[vol.trader_id()] = vol
        self.__history_limit_order[order.order_id()] = order
        vol.dump()
        # 判断是开仓还是平仓
        if vol.comb_offset_flag() == CombOffset.open: # 开仓
            if vol.direction() == Direction.buy_direction: # 多头仓
                # self.long_volumes[vol.symbol()] = vol
                self.long_volumes[vol.trader_id()] = vol
            else: # 空头仓
               # self.short_volumes[vol.symbol()] = vol
                self.short_volumes[vol.trader_id()] = vol
            self.__account.open_cash(order.margin(),vol.margin(), order.fee(), vol.fee())
        else: # 平仓
            # pdb.set_trace()
            MLog.write().debug("close position account:")
            if vol.direction() == Direction.buy_direction: # 平空头仓
                if self.short_volumes.has_key(order.hold_volume_id()):
                    v = self.short_volumes[order.hold_volume_id()]
                    # self.__account.set_close_profit(v,vol)
                    del self.short_volumes[order.hold_volume_id()]
            else: # 平多头仓
                if self.long_volumes.has_key(order.hold_volume_id()):
                    v = self.long_volumes[order.hold_volume_id()]
                    # self.__account.set_close_profit(v,vol)
                    del self.long_volumes[order.hold_volume_id()]
            self.__account.close_cash(v,vol,order.fee())
        self.__account.dump()

    def on_order(self, order):
        if order.status() == OrderStatus.all_traded:
            MLog.write().debug('order is all traded')
        self.__limit_order[order.order_id()] = order
        self.__history_limit_order[order.order_id()] = order
    
    def on_bar(self, bar):
        self.__bar_list.append(bar)       

        # 休盘的最后两分钟平仓
        if len(self.__bar_list) < 5:
            return
        if len(self.__bar_list) > 5:
            self.__bar_list.pop(0)
        
        next_price = self.__on_fc_single()
        close_price = self.__bar_list[-1].close_price()

        # 距行情结束还有5分钟则全部平仓
        if bar.current_time() > time.mktime(datetime.datetime(bar.mktime() / 10000,bar.mktime() / 100 % 100, bar.mktime() % 100,14,55,00).timetuple()):
            MLog.write().debug("time out start close position")
            if len(self.short_volumes) > 0:
                for k,v in self.short_volumes.items():
                    order = self.__short_close(bar.last_sell_price(), v.amount(),bar.current_time())
                    order.set_hold_volume_id(v.trader_id())
                    self.__account.insert_order_cash(order.margin(), order.fee())
                    self.__working_limit_order[order.order_id()] = order
                    self.__limit_order[order.order_id()] = order
                    order.dump()
            if len(self.long_volumes) > 0: 
                for k,v in self.long_volumes.items():
                    order = self.__long_close(bar.last_buy_price(), v.amount(), bar.current_time())
                    order.set_hold_volume_id(v.trader_id())
                    self.__account.insert_order_cash(order.margin(), order.fee())
                    self.__working_limit_order[order.order_id()] = order
                    self.__limit_order[order.order_id()] = order
                    order.dump()
            return 

        # pdb.set_trace()
        # 多仓，空仓判断
        if close_price < next_price: # 多仓信号
            MLog.write().debug("long singal start")
            self.__long_operation(next_price, self.__bar_list[-1], DEFAULT_AMOUNT)
        elif close_price > next_price: # 空仓信号
            MLog.write().debug("short singal start")
            self.__short_operation(next_price, self.__bar_list[-1], DEFAULT_AMOUNT)
        
