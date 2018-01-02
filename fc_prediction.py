# coding: utf-8

import tensorflow as tf
import fc_inference
import os
import argparse
import csv
import numpy as np
import pandas as pd
from data_sets import DataSets, GFDataSet, PDataSet
import pdb
from sklearn.preprocessing import MinMaxScaler

INPUT_NODE = 10 * 4

FLAGS = None


GLOBAL_COUNT = 0

class Prediciton(object):

    def init_model(self, time_step,  model_file):
        self.__x = tf.placeholder(dtype=tf.float32, shape=[None,time_step, INPUT_NODE])
        self.__y = tf.placeholder(dtype=tf.float32, shape=[None, time_step, fc_inference.n_target])

        reshape_x = tf.reshape(self.__x,[-1, INPUT_NODE])
        
        self.__y_ = fc_inference.chg_inference(reshape_x, None, None, False)
        self.__y_reshape = tf.reshape(self.__y,[-1])

        saver = tf.train.Saver(tf.global_variables())

        init = tf.global_variables_initializer()
        self.__sess = tf.Session()
        self.__sess.run(init)
        latest_checkpoint = tf.train.latest_checkpoint(model_file)
        saver.restore(self.__sess,latest_checkpoint)

        self.__out_list = []
        self.__yt_list = []

    
    def prediction_price(self, data_set_x,time_step):        
        out = self.__sess.run([self.__y_], feed_dict={self.__x:data_set_x[0:1]})
        return out

    def prediction(self, data_sets):
        while data_sets.is_range():
            data_set = data_sets.batch()
            batch_index, test_x, test_y = data_set.test_batch()
            for step in range(len(batch_index) - 1):
                out,yt = self.__sess.run([self.__y_,self.__y_reshape],feed_dict={self.__x:test_x[batch_index[step]:batch_index[step + 1]],
                                                                                 self.__y:test_y[batch_index[step]:batch_index[step + 1]]})
                self.__out_list.append(np.squeeze(np.array(out)).T)
                self.__yt_list.append(yt.T)

    def save(self):
        df_out = pd.DataFrame(np.array(self.__out_list[0:1]).T)
        df_yt = pd.DataFrame(np.array(self.__yt_list[0:1]).T)

        df_out.to_csv("df_out1.csv", encoding = "utf-8")
        df_yt.to_csv("df_yt1.csv", encoding = "utf-8")

    def new_signal(self, data_sets):
        data_sets = np.column_stack((data_sets,data_sets[:,6] - data_sets[:,4]))
        
        #lbsp_avg 买卖盘平均价
        data_sets = np.column_stack((data_sets, (data_sets[:,6] + data_sets[:,4])/2))
        #lbs_deep 买卖盘深度
        data_sets = np.column_stack((data_sets,data_sets[:,5] + data_sets[:,7]))
        #lbsv_diff 买卖盘委量差
        data_sets = np.column_stack((data_sets, data_sets[:,7] - data_sets[:,5]))
        t_close = data_sets[:,0][1:]
        y_close = data_sets[:,0][:-1]
        risk_fail = ((t_close - y_close) / y_close) 
        first = np.array([0.])
        risk_fail = np.concatenate((first, risk_fail), axis=0)
    
        data_sets = np.column_stack((data_sets, risk_fail))


        # 删除无效列
        data_sets = np.delete(data_sets,[4,5,6,7], axis=1)
        
        input_data = data_sets[0:4,]
        current_data = data_sets[4,]
        
        #标准化
        close_price = current_data[0]
        input_data[:,0:4] = np.log(input_data[:,0:4] / close_price)
        input_data[:,5] = np.log(input_data[:,5] / close_price)
    
        #归一化
        for i in range(input_data.shape[1]):
            input_data[:,i] = (input_data[:,i] - input_data[:,i].min()) / (input_data[:,i].max() - input_data[:,i].min()) 



        input_data = np.nan_to_num(input_data)
        input_data = input_data.reshape(-1, 4 * input_data.shape[1])

        input_data_x = []
        input_data_x.append(input_data)

        out = self.prediction_price(input_data_x,1)
        return np.squeeze(np.array(out[0:1]))

    def signal(self, data_set, model_file):
        mean_data = np.mean(data_set, axis=0)
        std_data = np.std(data_set, axis=0)
        normalized_data = (data_set - mean_data) / std_data
        normalized_data = np.nan_to_num(normalized_data)
        scaler = MinMaxScaler()
        scaler.fit(normalized_data)
        normalized_data = scaler.transform(normalized_data)
        input_data = normalized_data[0:4,].reshape(-1,16)
        input_data_x = []
        input_data_x.append(input_data)
        out = self.prediction_price(input_data_x,1, model_file)
        pred_price = np.squeeze(np.array(out[0:1])) * std_data[0] + mean_data[0]
        # return pred_price  - np.squeeze(data_set[4:,0:1])
        return pred_price


def test_one():
    model_file = '/kywk/strategy/model/close_price_4/model/'
    # data_set = np.array([[3300,3301,3298,3301],[3297,3300,3296,3299],[3297,3299,3296,3297],[3295,3298,3294,3297]])
    # data_set = np.array([[3286,3286,3275,3276],[3281,3286,3280,3285],[3283,3291,3280,3281],[3281,3286,3279,3283],[3285,3287,3280,3281]])
    
    j = 100
    while j > 0:
        data_set = np.array([[3280,3281,3280,3281],[3281,3281,3280,3281],[3280,3281,3280,3281],[3282,3283,3280,3280],[3282,3283,3282,3282]])
        pred = Prediciton()
        print pred.signal(data_set,model_file)
        j -= 1


def test_two():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--dir',type=str,help = 'data dir')
    # FLAGS, unparsed = parser.parse_known_args()

    '''
    for path, dirs, fs in os.walk('./../fc/data/out_dir/ag/ag2017/'):
        for f in fs:
            data_set = PDataSet()
            data_set.calc_etf(os.path.join(path,f))
            pred = Prediciton()
            loss = pred.prediction(data_set,data_set.test_step(),model_file)
            print loss
    '''


def test_three():
    model_file = './../test/model/'
    data_sets = np.array([[3303.0,3303.0,3303.0,3303.0,3303.0,270.0,3304.0,75.0,1620.0],
                         [3306.0,3308.0,3304.0,3305.0,3305.0,1035.0,3306.0,1650.0,62280.0],
                         [3304.0,3306.0,3302.0,3306.0,3303.0,1425.0,3304.0,255.0,34440.0],
                         [3304.0,3305.0,3303.0,3304.0,3304.0,2580.0,3305.0,2670.0,22650.0],
                         [3303.0,3305.0,3303.0,3304.0,3303.0,3360.0,3304.0,975.0,18900.0]])


    pred = Prediciton()
    pred.init_model(1,model_file)
    j = 100
    while j > 0:
        print pred.new_signal(data_sets)
        j -= 1
    # print input_data

def test_four():
    model_file = './../../result/20171231/model/'
    pred = Prediciton()
    pred.init_model(55, model_file)
    data_sets = DataSets()
    data_sets.gf_etf('./../../data/out_dir/temp/')
    pred.prediction(data_sets)
    pred.save()

def main(argv=None):
    test_four()


if __name__ == '__main__':
    tf.app.run()
