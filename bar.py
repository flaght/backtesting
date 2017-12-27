#!/usr/bin/env python
# coding=utf-8

from mlog import MLog
'''
K线数据
'''
class Bar(object):
    def __init__(self):
        self.__symbol = ''
        self.__exchange = ''
        self.__current_time = 0 # 成交时间
        self.__new_price = 0.0 # 最新价
        self.__open_price = 0.0 # 开盘价
        self.__close_price = 0.0 # 收盘价
        self.__high_price = 0.0 # 最高价
        self.__low_price = 0.0 # 最低价
        self.__volume = 0 # 成交量 
        self.__amount = 0.0  #成交额
        self.__inner_vol = 0.0 # 内盘成交量
        self.__tick__count = 0.0 # 累计成交笔数
        self.__open_interset = 0 # 持仓量
        self.__settle_price = 0.0 # 结算价
        self.__last_sell_price = 0.0 #最后一笔卖一价
        self.__last_buy_price = 0.0 # 最后一笔买一价
        self.__last_sell_vol = 0 #最后一笔卖一量
        self.__last_buy_vol = 0 # 最后一笔买一量
        self.__mktime = 0 # 交易日

    def set_pd(self, pd):
        self.__current_time = pd[15]
        self.__open_price = pd[6]
        self.__close_price = pd[1]
        self.__high_price = pd[3]
        self.__low_price = pd[4]
        self.__volume = pd[16]
        self.__last_sell_price = pd[13]
        self.__last_buy_price = pd[11]
        self.__last_sell_vol = pd[14]
        self.__last_buy_vol = pd[12]
        self.__mktime = pd[5]
    def dump(self):
        MLog.write().debug("current_time:%d open_price:%f close_price:%f high_price:%f low_price:%f volume:%d, last_sell_price:%f, last_buy_price:%f, last_sell_vol:%d, last_buy_vol:%d" %(self.__current_time,
            self.__open_price, self.__close_price, self.__high_price, self.__low_price,
            self.__volume, self.__last_sell_price, self.__last_buy_price, self.__last_sell_vol,
            self.__last_buy_vol))


    def set_symbol(self, symbol):
        self.__symbol = symbol

    def set_exchange(self, exchange):
        self.__exchange = exchange

    def set_current_time(self, current_time):
        self.__current_time = current_time

    def set_new_price(self, new_price):
        self.__new_price = new_price

    def set_open_price(self, open_price):
        self.__open_price = open_price

    def set_close_price(self, close_price):
        self.__close_price = close_price

    def set_high_price(self, high_price):
        self.__high_price = high_price

    def set_low_price(self, low_price):
        self.__low_price = low_price

    def set_volume(self, volume):
        self.__volume = volume

    def set_amount(self, amount):
        self.__amount = amount

    def set_inner_vol(self, inner_vol):
        self.__inner_vol = inner_vol

    def set_tick_count(self, tick_count):
        self.__tick__count = tick_count

    def set_open_interset(self, open_interset):
        self.__open_interset = open_interset

    def set_settle_price(self, settle_price):
        self.__settle_price = settle_price

    def set_last_sell_price(self, last_sell_price):
        self.__last_sell_price = last_sell_price

    def set_last_buy_price(self, last_buy_price):
        self.__last_buy_price = last_buy_price

    def set_mktime(self,mktime):
        self.__mktime = mktime

    def symbol(self):
        return self.__symbol

    def exchange(self):
        return self.__exchange

    def current_time(self):
        return self.__current_time
    
    def mktime(self):
        return self.__mktime
    
    def new_price(self):
        return self.__new_price

    def open_price(self):
        return self.__open_price

    def close_price(self):
        return self.__close_price

    def high_price(self):
        return self.__high_price

    def low_price(self):
        return self.__low_price

    def volume(self):
        return self.__volume

    def amount(self):
        return self.__amount

    def inner_vol(self):
        return self.__inner_vol

    def tick_count(self):
        return self.__tick_count

    def open_interset(self):
        return self.__open_interset

    def settle_price(self):
        return self.__settle_price

    def last_sell_price(self):
        return self.__last_sell_price

    def last_buy_price(self):
        return self.__last_buy_price
