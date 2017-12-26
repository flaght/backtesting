#!/usr/bin/env python
# coding=utf-8

from collections import OrderedDict
import copy

class DailyRecord(object):
    def __init__(self):
        self.__mkdate = 0 # 交易日
        self.__account_id = ''
        
        
        self.__interests = 0.0  # 上日结存 + 平仓盈亏 + 浮动盈亏(持仓盈亏) + 出入金 - 手续费 
        self.__profit = 0.0 # 当日盈亏
        self.__value = 0.0 # 当日净值 
        self.__value_chg = 0.0 # 涨跌幅
        self.__retracement = 0.0 # 最大回撤

        self._available_cash = 0.0 # 当日初始可用资金
        self.__close_profit = 0.0  # 平仓收益
        self.__position_profit = 0.0 # 持仓收益
        self.__commission = 0.0 # 手续费
        self.__max_profit = 0.0 # 历史中最大收益
        self.__history_limit_volume = OrderedDict() # 交易记录
        self.__history_limit_order = OrderedDict() # 委托订单


    def set_account_id(self, account_id):
        self.__account_id = account_id

    def set_close_profit(self, close_profit):
        self.__close_profit = close_profit

    def set_position_profit(self, position_profit):
        self.__position_profit = position_profit

    def set_commssion(self, commssion):
        self.__commission = commssion

    def set_limit_volume(self, limit_volume):
        self.__history_limit_volume = copy.deepcopy(limit_volume)

    def set_limit_order(self,limit_order):
        self.__history_limit_order = copy.deepcopy(limit_order)


    def set_available(self, available_cash):
        self.__available_cash = available_cash

    def all_profit(self):
        self.__profit = self.__close_profit + self.__position_profit  - self.__commission # 当日盈亏
        return self.__profit

    def calc_result(self):
        self.__interests = self.__available_cash + self.__profit #每日权益
        self.__value =  self.__interests / self.__available_cash 
        self.__retrace_ment = ((self.__profit - self.__max_profit)) / (self.__max_profit + self.__available_cash)


    def dump(self):
        print('interests:%f,profit:%f,value:%f,retracement:%f'%(self.__interests, 
                self.all_profit(), self.__value, self.__retracement))
