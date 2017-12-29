# coding: utf-8

import tensorflow as tf
import fc_inference
import os
import argparse
import csv
import numpy as np
from data_sets import DataSets, GFDataSet, PDataSet
import pdb
from sklearn.preprocessing import MinMaxScaler

INPUT_NODE = 10 * 4

FLAGS = None


GLOBAL_COUNT = 0

class Prediciton(object):
    def prediction(self, data_sets, time_step):
        x = tf.placeholder(dtype=tf.float32, shape=[None,time_step, INPUT_NODE])
        y = tf.placeholder(dtype=tf.float32, shape=[None, time_step, fc_inference.n_target])

        reshape_x = tf.reshape(x,[-1, INPUT_NODE])
        
        global GLOBAL_COUNT

        if GLOBAL_COUNT == 0:
            y_ = fc_inference.chg_inference(reshape_x, None, None, False)
        else:
            y_ = fc_inference.chg_inference(reshape_x,None,None,True)

        GLOBAL_COUNT += 1
        
        cross_entroy_mean = tf.reduce_mean(tf.square(tf.reshape(y_,[-1]) - tf.reshape(y, [-1])))

        test_x, test_y = data_sets.test_batch()

        saver = tf.train.Saver(tf.global_variables())

        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            model_file = tf.train.latest_checkpoint('/kywk/strategy/model/close_price_4/model/')
            saver.restore(sess, model_file)
            mse_final, out = sess.run([cross_entroy_mean, y_],
                                  feed_dict={x: test_x[0:1],
                                             y: test_y[0:1]
                                             }
                                  )
            return mse_final
    
    def prediction_price(self, data_set_x,time_step, model_file):
        
        x = tf.placeholder(dtype=tf.float32, shape=[None,time_step, INPUT_NODE])
        reshape_x = tf.reshape(x,[-1, INPUT_NODE])
        global GLOBAL_COUNT

        GLOBAL_COUNT += 1
        if GLOBAL_COUNT == 1:
            y_ = fc_inference.chg_inference(reshape_x, None, None, False)
        else:
            y_ = fc_inference.chg_inference(reshape_x,None,None,True)

        saver = tf.train.Saver(tf.global_variables())
        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            model_file = tf.train.latest_checkpoint(model_file)
            saver.restore(sess, model_file)
            out = sess.run([y_], feed_dict={x: data_set_x[0:1]})
            return out


    def new_signal(self, data_sets, model_file):
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

        out = self.prediction_price(input_data_x,1, model_file)
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
    print pred.new_signal(data_sets,model_file)

    # print input_data

def main(argv=None):
    test_three()


if __name__ == '__main__':
    tf.app.run()
