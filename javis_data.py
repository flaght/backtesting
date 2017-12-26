
# coding: utf-8

import tensorflow as tf
import pandas as pd
import time
import os
import json
import csv
import pdb
from operator import add
from javis import Client
class PutOrder:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.buy_price = []
        self.sell_price = []
        self.buy_vol = []
        self.sell_vol = []
    
    def set_order(self,buy_price, sell_price, buy_vol, sell_vol):
        self.buy_price.append(buy_price)
        self.sell_price.append(sell_price)
        self.buy_vol.append(buy_vol)
        self.sell_vol.append(sell_vol)
        
    def is_empty(self):
       return 0 if len(self.buy_price) > 0 else 1

    #委托的买盘平均价格
    def __avg_buy_price(self):
        if len(self.buy_price) == 0:
            return 0.0
        return float(reduce(add, self.buy_price)) / len(self.buy_price)
    
    #委托的卖盘平均价格
    def __avg_sell_price(self):
        if len(self.sell_price) == 0:
            return 0.0
        return float(reduce(add, self.sell_price)) / len(self.sell_price)
    
    #委托的买盘最后价格
    def __last_buy_price(self):
        return float(self.buy_price[-1])
    
    #委托的卖盘最后价格
    def __last_sell_price(self):
        return float(self.sell_price[-1])
    
    #委托主买量
    def __all_buy_vol(self):
        return reduce(add, self.buy_vol)
    
    #委托主卖量
    def __all_sell_vol(self):
        return reduce(add, self.sell_vol)
    
    #委托主买平均量
    def __avg_buy_vol(self):
        if len(self.buy_vol) == 0:
            return 0.0
        return float(self.__all_buy_vol()) / len(self.buy_vol)
    
    #委托主卖平均量
    def __avg_sell_vol(self):
        if len(self.buy_vol) == 0:
            return 0.0
        return float(self.__all_sell_vol()) / len(self.sell_vol)
    
    #委托主买最后一笔量
    def __last_buy_vol(self):
        if len(self.buy_vol) == 0:
            return 0
        return float(self.buy_vol[-1])
    
    #委托主卖最后一笔量
    def __last_sell_vol(self):
        if len(self.sell_vol) == 0:
            return 0
        return float(self.sell_vol[-1])
        
    def get_unit(self,unit):
        unit['pabp'] = self.__avg_buy_price() #委托的买盘平均价格
        unit['pasp'] = self.__avg_sell_price() #委托的卖盘平均价格
        unit['plbp'] = self.__last_buy_price() #委托的买盘最后一刻价格
        unit['plsp'] = self.__last_sell_price() #委托的卖盘最后一刻价格
        unit['pabv'] = self.__avg_buy_vol()#委托的买盘平均量
        unit['pasv'] = self.__avg_sell_vol()#委托的卖盘平均量
        unit['plbv'] = self.__last_buy_vol()#委托的买盘最后量
        unit['plsv'] = self.__last_sell_vol()#委托的卖最后量
        return unit

class TickFile:
    def __init__(self):
        self.full_path = None
        self.volume = None
        self.date = None
        self.filename = None

    def set_full_path(self, full_path):
        self.full_path = full_path

    def set_volume(self, volume):
        self.volume = volume

    def set_date(self, date):
        self.date = date

    def set_filename(self, filename):
        self.filename = filename

class Dominant:
    def __init__(self):
        self.dict = {}
    
    def set_tick_file(self, tick_file):
        value = []
        if self.dict.has_key(tick_file.date):
            value = self.dict.get(tick_file.date) 
        value.append(tick_file)
        self.dict[tick_file.date] = value

    def tick_file_record(self,filename):
        file_dominant = filename + ".csv"
        fdominant = open(file_dominant,'w')
        fieldnames = ['name','path','volume','date']
        dominant_writer = csv.DictWriter(fdominant, fieldnames=fieldnames)
        dominant_writer.writeheader()
        for k in self.dict:
            tick_file_list = self.dict.get(k)
            filename = "./record/" + str(k) + ".csv"
            #output = open(filename, 'w+')
            with open(filename, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                best_tick_file = None
                for tick_file in tick_file_list:
                    writer.writerow({'name':tick_file.filename,'path':tick_file.full_path, 'volume': tick_file.volume, 'date':tick_file.date})
                    if best_tick_file == None:
                        best_tick_file = tick_file
                    elif best_tick_file.volume < tick_file.volume:
                        best_tick_file = tick_file
                dominant_writer.writerow({'name':best_tick_file.filename,'path':best_tick_file.full_path, 'volume': best_tick_file.volume, 'date':best_tick_file.date})


class JavisData:
    
    def __init__(self):
        self.dominant = Dominant()

    def create_javis(self, uid, token):
        self.client = Client()
        self.client.set_user(uid, token)

    def read_local_data(self, filename):
        ob = json.loads(open(filename,'r+').read())
        trade_data = ob.get('dt')
        for unit in trade_data:
            print "time:" + str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(unit.get('ct')))))
            print "open price:" + str(unit.get('op'))
            print "high price:" + str(unit.get('hp'))
            print "low price:" + str(unit.get('lp'))
            print "new price:" + str(unit.get('np'))
            print "volume:" + str(unit.get('vl'))
            print "amount:" + str(unit.get('ao'))
            print "=======>"

    def read_data(self, symbol, start_time, end_time):
        trade_data = self.client.dyna_tick(symbol, start_time, end_time)
        for unit in trade_data:
            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(unit.get('ct'))))
            print unit.get('bp1')
            print unit.get('sp1')
            print unit.get('bv1')
            print unit.get('sv1')
            print unit.get('bp2')
            print unit.get('sp2')
            print unit.get('bv2')
            print unit.get('sv2')
            print "=======>"
        
    def __read_data_sets(self, symbol, start_time, end_time):
        return self.client.dyna_tick(symbol, start_time, end_time)
    
    def __init_bar(self,unit): #初始化
        bar_unit = {}
        bar_unit['open'] = unit.get('np')
        bar_unit['high'] = unit.get('np')
        bar_unit['low'] = unit.get('np')
        bar_unit['close'] = unit.get('np')
        bar_unit['time'] = unit.get('ct') / 60 * 60
                
        #成交量
        bar_vol = unit.get('vl')
        last_date_vol = unit.get('vl')
                
        bar_unit['date'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(unit.get('ct') / 60 * 60)))
        bar_unit['mtd'] = unit.get('md')
        bar_minute = unit.get('ct') / 60 * 60
        return bar_unit,bar_vol,last_date_vol,bar_minute
        

    def __on_trade_bar(self, trade_data): 
         #[开盘价，收盘价，最高价，最低价，成交量，买卖盘报价平均价格，委买委卖量之比，主买量，主卖量]
        #新的交易日判断
        bar_minute = 0
        bar_vol = 0.0
        bar_unit = None
        bar_list = []
        last_minute_vol = 0.0
        last_date_vol = 0.0
        last_market_date = 0
        bar_vol = 0.0
        put_order = PutOrder()
        for unit in trade_data:
            if last_market_date==0 or last_market_date != unit.get('md'):#新的交易日
                if last_market_date != 0: 
                    vol = last_date_vol - last_minute_vol
                    bar_unit['vol'] = vol
                    bar_unit = put_order.get_unit(bar_unit)
                    put_order.reset()
                    bar = bar_unit
                    bar_list.append(bar)
                    last_date_vol = 0
                    last_minute_vol = 0
                
                last_market_date = unit.get('md')
                bar_unit,bar_vol,last_date_vol,bar_minute = self.__init_bar(unit)
                put_order.set_order(unit.get('bp1'), unit.get('sp1'), unit.get('bv1'),unit.get('sv1'))
            else:
                if (bar_minute != unit.get('ct') / 60 * 60 or bar_minute == 0):
                    if bar_minute != 0:
                        bar_unit['vol'] = bar_vol - last_minute_vol
                        bar_unit = put_order.get_unit(bar_unit)
                        put_order.reset()
                        bar = bar_unit
                        bar_list.append(bar)
                        last_minute_vol = bar_vol
                    bar_unit,bar_vol,last_date_vol,bar_minute = self.__init_bar(unit)
                    put_order.set_order(unit.get('bp1'), unit.get('sp1'), unit.get('bv1'),unit.get('sv1'))
                else:
                    bar = bar_unit
                    bar['high'] = max(bar_unit.get('high'),unit.get('np'))
                    bar['low'] = min(bar_unit.get('low'),unit.get('np'))
                    bar['close'] = unit.get('np')
                    
                    last_date_vol = unit.get('vl')
                    bar_vol = unit.get('vl')
                    bar_unit = bar
                    put_order.set_order(unit.get('bp1'), unit.get('sp1'), unit.get('bv1'),unit.get('sv1'))
        
        if put_order.is_empty()  == 0:#不为空
            vol = last_date_vol - last_minute_vol
            bar_unit['vol'] = vol
            bar_unit = put_order.get_unit(bar_unit)
            put_order.reset()
            bar = bar_unit
            bar_list.append(bar)

        return bar_list
            
    def __get_data_pd(self, symbol, start_time, end_time):
        return pd.DataFrame(self.__on_trade_bar(self.__read_data_sets(symbol, start_time, end_time)))
    
    def __write_file(self, filename, symbol,start_time,end_time):
        pd_data = self.__get_data_pd(symbol, start_time, end_time)
        s = os.path.split(filename)
        if not os.path.exists(s[0]):
            os.makedirs(s[0])
        pd_data.to_csv(filename, encoding = "utf-8")
   
    def __calcu_file_volume(self, filename):
        f = open(filename, 'r+')
        ob = json.loads(f.read())
        f.close()
        return ob.get('dt')[-1].get('vl')
    
    def __traversed(self,dir):
        dict = {}
        for path, dirs, fs in os.walk(dir):
            list = []
            for f in fs:
                list.append(os.path.join(path,f))
            dict[path] = list
        return dict
    
    def __calc_dominant(self, full_path):
        name = os.path.split(full_path)[-1].split('_')[-1]
        filename = os.path.split(full_path)[-1].split('_')[0]
        date = name.split('.')[0]
        volume = self.__calcu_file_volume(full_path)
        tick_file = TickFile()
        tick_file.set_full_path(full_path)
        tick_file.set_volume(volume)
        tick_file.set_date(date)
        tick_file.set_filename(filename)
        return tick_file

    def calc_dominant(self, dir, filename):
        dict = self.__traversed(dir)
        for key in dict:
            print key
            for v in dict[key]:
                tick_file = self.__calc_dominant(v)
                self.dominant.set_tick_file(tick_file)

        self.dominant.tick_file_record(filename)

    def write_file(self, dir, symbol,start_time,end_time):
        filename = dir + 'data/' +  symbol.split('.')[0] + '_'+ start_time.split(' ')[0] + '_' + end_time.split(' ')[0] + ".jcsv"
        self.__write_file(filename, symbol,start_time,end_time)
        
    def get_data_pd(self, dir, symbol, start_time, end_time):
        filename = dir + 'data/' +  symbol.split('.')[0] + '_'+ start_time.split(' ')[0] + '_' + end_time.split(' ')[0] + ".jcsv"
        #self.log.log().debug('filename: %s',filename)
        #检测本地是否存储
        if not os.path.isfile(filename):
            self.__write_file(filename, symbol,start_time,end_time)
        return pd.read_csv(filename, sep =',')

    def send_data_pd(self,symbol,start_time, end_time):
        return self.client.dyna_file(symbol, start_time, end_time)
    
    def read_data_pd(self,filename):
        ob = json.loads(open(filename,'r+').read())
        return pd.DataFrame(self.__on_trade_bar(ob.get('dt')))


    # 将jcvs的数据转化为cvs的bar数据
    def tick_to_bar(self, dir, out_dir):
        for path, dirs, fs in os.walk(dir):
            for f in fs:
                df = self.read_data_pd(os.path.join(path,f))
                filename =f.split('.')[0] + '.csv'
                print filename
                df.to_csv(str(out_dir) + '/' + str(filename), encoding = "utf-8")

    #指定目录将tick数据转化为bar数据
    def check_data_file(self, filename, f):
        df = pd.read_csv(filename, header=None, sep=',', names=["close","date","high","low","mtd","open","pabp","pabv","pasp","pasv","plbp","plbv","plsp","plsv","time","vol"])
        print "date:" + df.iloc[-1]['date'] +" close price:" + df.iloc[-1]['close'] + "  open price:" + df.iloc[-1]['open'] +  " low price:" + df.iloc[-1]['low'] + " high price:" + df.iloc[-1]['high'] + " file:" + f

    def check_data_dir(self, dir):
        for path, dirs, fs in os.walk(dir):
            for f in fs:
                self.check_data_file(os.path.join(path, f),f)


    def build_dominat_bar(self, filename, out_dir):
        df = pd.read_csv(filename, header=None, sep=',', names=["name","path","volume","date"])
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        for indexs in df.index:
            if indexs != 0:
                out_file = out_dir + "/" + df.loc[indexs].values[0] + "_" + df.loc[indexs].values[3] + ".csv"
                if os.path.isfile(out_file):
                    os.remove(out_file)
                self.read_data_pd(df.loc[indexs].values[1]).to_csv(out_file)

if __name__ == '__main__':
    uid = 142
    token = 'adc28ac69625652b46d5c00b'
    symbol = 'ag1601.SHFE'
    start_time = '2016-1-15 14:01:12'
    end_time = '2016-1-15 15:10:00'
    dir = './test'
    clt =  JavisData(uid, token)
    clt.read_local_data('/kywk/strategy/strange/future/142/ag1706/ag1706_20161026.jcsv')
    #clt.read_data(symbol, start_time, end_time)
    #print clt.read_data_pd(dir, symbol, start_time, end_time)
    #print clt.read_data_pd('../strange/data/ag1601_20160114.jcsv')
    #clt.calcu_dominant('/kywk/strategy/strange/future/142')
    #clt.calcu_dominant('./data/temp/')
    print "end==>"

