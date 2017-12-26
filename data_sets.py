# -*- coding: utf-8 -*-
# Copyright 2017 The Strange Authors. All Rights Reserved.
import numpy as np
import pandas as pd
import os
import math
import pdb
from sklearn.preprocessing import MinMaxScaler


class DataSets(object):
    def __init__(self):
        self._data_sets = []
        self._index_in_epoch = 0

    def is_range(self):
        return 1 if self._index_in_epoch < len(self._data_sets) else 0
    
    def reset(self):
        self._index_in_epoch = 0

    def gf_etf(self, cur_dir):
        for path, dirs, fs in os.walk(cur_dir):
            for f in fs:
                data_sets = PDataSet()
                data_sets.calc_etf(os.path.join(path, f))
                self._data_sets.append(data_sets)

    def train_batch(self):
        data_set = self._data_sets[self._index_in_epoch]
        self._index_in_epoch+=1
        return data_set

class PDataSet(object):

    def __init__(self, dim=4, next_time=1, batch_size=50, train_step=55, test_step=1000):
        self._x_train = []
        self._y_train = []
        self._batch_index_train = []
        self._x_test = []
        self._y_test = []
        self._batch_size = batch_size
        self._train_step = train_step
        self._test_step = test_step
        self._dim = dim
        self._next_time = next_time
        self._file_name = ""

    def batch_size(self):
        return self._batch_size

    def train_step(self):
        return self._train_step

    def test_step(self):
        return self._test_step

    # 当前时间的前4个记录,预测当前时间的下个时间的最高价
    def _calc_price_data(self, data_train, data_test):

        # 标准差标准化(观察值减去平均数，再除以标准差)
        normalized_train_data = (data_train - np.mean(data_train, axis=0)) / np.std(data_train, axis=0)
        normalized_test_data = (data_test - np.mean(data_test, axis=0)) / np.std(data_test, axis=0)
        
        scaler = MinMaxScaler()
        scaler.fit(normalized_train_data)

        #归一化
        normalized_train_data = scaler.transform(normalized_train_data)
        normalized_test_data = scaler.transform(normalized_test_data)

        # normalized_train_data = data_train
        # normalized_test_data = data_test

        for i in range(len(data_train) - self._train_step - self._dim - 1):
            if i % self._batch_size == 0:
                self._batch_index_train.append(i)
            for u in range(self._train_step):
                if u == 0:
                    x = normalized_train_data[u + i:u + i + self._dim, :].reshape(-1, self._dim * data_train.shape[1])
                else:
                    t = normalized_train_data[u + i:u + i + self._dim, :].reshape(-1, self._dim * data_train.shape[1])
                    x = np.vstack((x, t))

            y = normalized_train_data[i + self._dim + self._next_time + 1:i + self._dim + self._next_time + 1 + self._train_step, 0, np.newaxis]
            #y = data_train[i + self._dim + self._next_time + 1:i + self._dim + self._next_time + 1 + self._train_step, 0, np.newaxis]
            self._x_train.append(x)
            self._y_train.append(y)

        test_step = self._test_step if (len(data_test) - 1) > self._test_step else (len(data_test) - 1)
        test_size = (len(normalized_test_data) + test_step - 1) // test_step

        for i in range(test_size-1):
            for u in range(test_step - self._dim - 1):
                if u == 0:
                    tx = normalized_test_data[u + i * test_step: u + i * test_step + self._dim,:].reshape(-1, self._dim * data_test.shape[1])
                else:
                    tt = normalized_test_data[u + i * test_step: u + i * test_step + self._dim,:].reshape(-1, self._dim * data_test.shape[1])
                    tx = np.vstack((tx,tt))
 
            ty = normalized_test_data[i * (test_step - self._dim) + self._dim + 1 + self._next_time:
                                       (i + 1) *(test_step - self._dim) + 1 + self._dim + self._next_time, 0, np.newaxis]
            
            # ty = data_test[i * (test_step - self._dim) + self._dim + 1 + self._next_time:
            #                           (i + 1) *(test_step - self._dim) + 1 + self._dim + self._next_time, 0, np.newaxis]
            self._x_test.append(tx)
            self._y_test.append(ty)
            self._test_step = test_step - self._dim - 1
    
    def file_name(self):
        return self._file_name

    def __calc_model_data(self, data):
        data = data.drop(
            ['Unnamed: 0', 'date', 'mtd', 'pabp', 'pabv', 'pasp', 'pasv', 'plbp', 'plbv', 'plsp', 'plsv', 'time',
             'vol'], 1)
        n = data.shape[0]

        data = data.values
        train_start = 0
        train_end = int(np.floor(0.8 * n))

        test_start = train_end + 1
        test_end = n

        data_train = data[np.arange(train_start, train_end), :]
        data_test = data[np.arange(test_start, test_end), :]
        
        #print  data_train
        #print '-------->'
        #print  data_test
        #print '-------->'
        #print  data
        self._calc_price_data(data_train, data_test)

    def train_batch(self):
        return self._batch_index_train, self._x_train, self._y_train

    def test_batch(self):
        return self._x_test, self._y_test

    def calc_etf(self, filename):
        #print filename
        self._file_name = filename
        data = pd.read_csv(filename)
        print filename
        self.__calc_model_data(data)


class GFDataSet(object):

    def __init__(self):
        self._x_train = []
        self._y_train = []
        self._x_test = []
        self._y_test = []
        self._index_in_epoch = 0  # 序列是从0开始的
        self._range = 4

    def __calc_feature(self, filename):
        data = pd.read_csv(filename)
        # 买卖盘报价差
        data['absp_diff'] = np.fabs(data['pasp'].values - data['pabp'].values)
        data['lbsp_diff'] = np.fabs(data['plsp'] - data['plbp'])

        # 买卖盘平均价格
        data['absp_avg'] = (data['pasp'] + data['pabp']) / 2
        data['lbsp_avg'] = (data['plsp'] + data['plbp']) / 2
        # 买卖盘深度
        data['lbs_deep'] = (data['plbv'] + data['plsv'])
        data['abs_deep'] = (data['pabv'] + data['pasv'])

        # 委买委卖量之差
        data['lbsv_diff'] = np.fabs(data['plsv'] - data['plbv'])
        data['absv_diff'] = np.fabs(data['pasv'] - data['pasv'])

        # 计算涨跌幅:(close - open) / open * 100%
        t_close = data['close'][1:]
        y_close = data['close'][:-1]
        risk_fail = ((t_close.values - y_close.values) / y_close.values) / 100
        first = np.array([0.])
        risk_fail = np.concatenate((first, risk_fail), axis=0)
        data['risk_fail'] = risk_fail
        data = data.drop(
            ['Unnamed: 0', 'date', 'time', 'mtd', 'pabp', 'pabv', 'pasp', 'pasv', 'absp_diff', 'absp_avg', 'absv_diff',
             'abs_deep'], 1)
        return data

    # 训练集和测试集
    def __calc_model_data(self, data):
        # 买卖盘数据采用最后记录
        time_step = 50
        n = data.shape[0]
        p = data.shape[1]

        data = data.values
        train_start = 0
        train_end = int(np.floor(0.8 * n))

        test_start = train_end + 1
        test_end = n
        data_train = data[np.arange(train_start, train_end), :]
        data_test = data[np.arange(test_start, test_end), :]

        normalized_train_data = (data_train - np.mean(data_train, axis=0)) / np.std(data_train, axis=0)
        # 构建训练 X and Y
        for i in range(len(data_train) - time_step):
            x = normalized_train_data[i:i + time_step, :-1]
            y = normalized_train_data[i:i + time_step, -1, np.newaxis]
            self._x_train.append(x)
            self._y_train.append(y)

        # 构建测试 X and Y
        test_time_step = test_end - test_start - 1
        normalized_test_data = (data_test - np.mean(data_test, axis=0)) / np.std(data_train, axis=0)

        size = (len(normalized_test_data) + test_time_step - 1) // test_time_step
        for i in range(size - 1):
            t_x = normalized_test_data[i * test_time_step:(i + 1) * test_time_step, :-1]
            t_y = normalized_test_data[i * test_time_step:(i + 1) * test_time_step, -1, np.newaxis]
            self._x_test.append(t_x)
            self._y_test.append(t_y)

    # 获取训练集
    def train_batch(self):
        return self._x_train, self._y_train

    # 获取测试集
    def test_batch(self):
        return self._x_test, self._y_test

    def calc_etf(self, filename):
        data = self.__calc_feature(filename)
        self.__calc_model_data(data)


if __name__ == '__main__':
    np.set_printoptions(threshold=np.inf)
    # data_sets = DataSets()
    # data_sets.gf_etf('./data/out_dir')
    # while data_sets.is_range():
    #    data_set = data_sets.train_batch()
    #    train_x,train_y = data_set.train_batch()
    #    test_x,test_y = data_set.test_batch()
    #    print("-------%s--------" %(data_set.file_name()))
    #    print(np.array(train_x[0:1]).shape)
    #    print(np.array(train_y[0:1]).shape)
    #    print(np.array(test_x[0:1]).shape)
    #    print(np.array(test_y[0:1]).shape)
    #    input = raw_input("Enter")
    #    print '-------------->'
    data_set = PDataSet()
    data_set.calc_etf('./data/out_dir/ag/ag2016/ag1612_20160906.csv')
    batch_index_train, train_x, train_y = data_set.train_batch()
    print batch_index_train
    print '-------->'
    print train_x[0:1]
    print '--------->'
    print train_y[0:1]
    # print len(train_x)
    # print len(train_y)
    # print '------------>'
    # print np.array(train_x[0:1])
    # print np.array(train_y[0:1]) 
    # print '----------->'
    # test_x, test_y = data_set.test_batch()
    # print np.array(test_x[0:1]).shape
    # print np.array(test_y[0:1]).shape
    # print np.array(train_x[0:1])
    # print '--------->'
    # print np.array(train_y[0:1])
    # data_set = GFDataSet()
    # filename = './data/out_dir/ag1606_20160104.csv'
    # data_set.calcu_etf(filename)
    # test_x,test_y = data_set.test_batchs()
    # train_x,train_y = data_set.train_batchs()
    # print np.array(train_x[0:1]).shape
    # print np.array(train_y[0:1]).shape
    # print np.array(test_x[0:1]).shape
    # print np.array(test_y[0:1]).shape
    # print np.squeeze(np.array(test_x[0:1])).shape
    # train_x,train_y = data_set.calcu_etf(filename)
    # print train_x[0:1]
    # print '--------->'
    # print train_y[0:1]
