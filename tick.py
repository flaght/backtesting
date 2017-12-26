#!/usr/bin/env python
# coding=utf-8


'''
Tick 数据
'''
class Tick(object):
    def __init__(self):
        self.__symbol = ''
        self.__exchange = ''
        self._current_time = 0 # 成交时间
        self.__new_price = 0.0 # 最新价
        self.__open_price = 0.0 # 开盘价
        self.__close_price = 0.0 # 收盘价
        self.__high_price = 0.0 # 最高价
        self.__clow_price = 0.0 # 最低价
        self.__volume = 0 # 成交量 
        self.__amount = 0.0  #成交额
        self.__inner_vol = 0.0 # 内盘成交量
        self.__tick__count = 0.0 # 累计成交笔数
        self.__open_interset = 0 # 持仓量
        self.__settle_price = 0.0 # 结算价
        
        self.__bid_price1 = 0.0 #买一
        self.__bid_price2 = 0.0
        self.__bid_price3 = 0.0
        self.__bid_price4 = 0.0
        self.__bid_price5 = 0.0

        self.__bid_vol1 = 0
        self.__bid_vol2 = 0
        self.__bid_vol3 = 0
        self.__bid_vol4 = 0
        self.__bid_vol5 = 0

        self.__ask_price1 = 0.0 # 卖一
        self.__ask_price2 = 0.0
        self.__ask_price3 = 0.0
        self.__ask_price4 = 0.0
        self.__ask_price5 = 0.0 

        self.__ask_vol1 = 0
        self.__ask_vol2 = 0
        self.__ask_vol3 = 0
        self.__ask_vol4 = 0
        self.__ask_vol5 = 0

