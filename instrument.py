#!/usr/bin/env python
# coding=utf-8

'''
期货合约
'''
class Instrument(object):
    def __init__(self):
        self.__product_class = 0 # 产品类型
        self.__delivery_year = 0 # 交割年份
        self.__delivery_month = 0 # 交割月份
        self.__max_market_order_volume = 0 # 市价单最大下单量
        self.__min_market_order_volume = 0 # 市价单最小下单量
        self.__max_limit_order_volume = 0 # 限价单最大下单量
        self.__min_limit_order_volume = 0 # 限价单最小下单量
        self.__volume_multiple = 0 # 合约数量乘数
        self.__price_tick = 0 # 最小变动价位
        self.__position_type = 0 # 持仓类型
        self.__position_data_type = 0 # 持仓日期类型
        self.__long_margin_ratio = 0.0 # 多头保证金
        self.__short_margin_ratio = 0.0 # 空头保证金
        self.__combination_type = 0 # 组合类型
        self.__instrument_id = '' # 合约代码
        self.__instrument_name = '' # 合约名称
        self.__create_date = '' # 创建日
        self.__open_date = '' # 上市日
        self.__expire_date = '' # 到期日
        self.__fee = 0.0 # 手续费
        self.__start_delive_date = '' # 开始交割日
        self.__end_delive_date = '' # 结束交割日

    # 合约名称
    def set_instrument_name(self, instrument_name):
        self.__instrument_name = instrument_name
    
    #合约ID
    def set_instrument_id(self, instrument_id):
        self.__instrument_id = instrument_id

    # 最小单位
    def set_min_limit_order_volume(self, min_limit_order_volume):
        self.__min_limit_order_volume = min_limit_order_volume

    # 最小变动价位
    def set_price_tick(self, price_tick):
        self.__price_tick = price_tick
    
    # 多头保证金
    def set_long_margin_ratio(self, long_margin_ratio):
        self.__long_margin_ratio = long_margin_ratio

    # 空头保证金
    def set_short_margin_ratio(self, short_margin_ratio):
        self.__short_margin_ratio = short_margin_ratio
    
    # 手续费
    def set_fee(self, fee):
        self.__fee = fee

    def min_limit_order_volume(self):
        return self.__min_limit_order_volume

    def price_tick(self):
        return self.__price_tick
    
    def long_margin_ratio(self):
        return self.__long_margin_ratio

    def short_margin_ratio(self):
        return self.__short_margin_ratio

    def fee(self):
        return self.__fee

    def instrument_name(self):
        return self.__instrument_name

    def instrument_id(self):
        return self.__instrument_id
