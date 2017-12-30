#!/usr/bin/env python
# coding=utf-8

from __future__ import division
from collections import OrderedDict
from bar import Bar
import pandas as pd
import os
from strange import Strange
from order import Direction, OrderStatus
from volume import Volume
from mlog import MLog

class LoopBack(object):

    def __init__(self):
        # self.__account = Account()
        # self.__account.set_init_cash(1000000)
        
        # self.__symbol = None # 交易标的

        self.__canncel_order = OrderedDict() # 撤销单
        self.__limit_order = OrderedDict() # 限价单
        self.__volume_order = OrderedDict() # 成交单

        # 价格撮合
        self.__working_limit_order = OrderedDict()
        
        self.__start_date = None # 回测开始时间
        self.__end_datae = None # 回测结束时间

        # 存储所有记录
        self.__log_list = []

        # 存储行情
        self.__history_data = OrderedDict()

        #降低内存使用 存储行情路径
        self.__history_file = OrderedDict()

        # 初始化策略
        self.__strategy = Strange(self.__working_limit_order)

    def set_symbol(self, symbol): # 期货为标的，非合约 如应输入ag而非ag1702
        self.__symbol = symbol

    def set_time(self,start_date, end_date):
        self.__start_date = start_date
        self.__end_datae = end_date

    def cross_limit_order(self, bar):
        buy_cross_price = bar.low_price() # 若买入方向限价单价格高于该价格，则会成交
        sell_cross_price = bar.high_price() # 若卖出方向限价单价格低于该价格，则会成交
        buy_best_cross_price = bar.open_price() # 在当前时间点前发出的买入委托可能的最优成交价
        sell_best_cross_price = bar.open_price() # 在当前时间点前发出的卖出委托可能的最优成交价

        #遍历所有的限价单
        for order_id, order in self.__working_limit_order.items():
            if order.status() == OrderStatus.not_traded:
                # 委托成功推送到策略
                order.set_status(OrderStatus.entrust_traded)
                self.__strategy.on_order(order)
            #判断是否会成交
            buy_cross = (order.direction() == Direction.buy_direction and
                        order.limit_price() >= buy_cross_price and 
                        buy_cross_price > 0)
            sell_cross = (order.direction() == Direction.sell_direction and 
                         order.limit_price()<=sell_cross_price and 
                         sell_cross_price > 0)

            if buy_cross or sell_cross:
                order.set_status(OrderStatus.all_traded)
                # 委托推送策略
                self.__strategy.on_order(order)
                
                vol = Volume()
                vol.create_trader_id()
                vol.set_symbol(order.symbol())
                vol.set_order_id(order.order_id())
                vol.set_direction(order.direction())
                vol.set_comb_offset_flag(order.comb_offset_flag())
                if buy_cross:
                    vol.set_limit_price(min(order.limit_price(),
                                            buy_best_cross_price))
                    vol.set_amount(order.amount())
                    vol.set_min_volume(order.min_volume())
                else:
                    vol.set_limit_price(max(order.limit_price(),
                                           sell_best_cross_price))
                    vol.set_amount(order.amount())
                    vol.set_min_volume(order.min_volume())

                vol.set_create_time(bar.current_time())
                vol.set_margin_ratio(order.margin_ratio())
                vol.set_fee(order.fee_ratio())
                self.__volume_order[vol.trader_id()] = vol
                # 成交推送策略
                self.__strategy.on_volume(vol, order)
                 
                if order_id in self.__working_limit_order:
                    del self.__working_limit_order[order_id]

    def __on_bar(self, data):
        bar = Bar()
        bar.set_pd(data)
        bar.set_symbol(self.__symbol)
        # 撮合限价单
        self.cross_limit_order(bar)
        # 推送给策略
        self.__strategy.on_bar(bar)
    
    def load_history_data(self, dominat_file):
        mkdate = os.path.split(dominat_file)[-1].split('_')[-1].split('.')[0]
        data = pd.read_csv(dominat_file)
        self.__history_data[mkdate] = data


    def load_history_dir(self, dir):
        for path, dirs, fs in os.walk(dir):
            for f in fs:
                dominat_file = os.path.join(path, f)
                mkdate = os.path.split(dominat_file)[-1].split('_')[-1].split('.')[0]
                self.__history_file[mkdate] = dominat_file
                # self.load_history_data(dominat_file)

        # 排序
        self.__history_file = OrderedDict(sorted(self.__history_file.items(), key=lambda t: t[0]))
        # for key,value in self.__history_file.items():
        #    print (key,value)


    def run_loop_back(self):
        for mkdate,file in self.__history_file.items():
            print file
            data = pd.read_csv(file)
            for index in data.index:
                self.__on_bar(data.loc[index].values)
            self.__strategy.record()

    def calc_result(self):
        self.__strategy.calc_result()

    def save(self):
        self.__strategy.save()

if __name__ == '__main__':
    MLog.config(name="look_back")
    lb = LoopBack()
    lb.set_symbol('ag')
    # lb.load_history_data('./../fc/data/out_dir/ag/ag2017/ag0001_20171121.csv')
    lb.load_history_dir('./../fc/data/out_dir/ag/ag2017/')
    lb.run_loop_back()
    # print('<----------------------------------->')
    lb.calc_result()
    # lb.save()
