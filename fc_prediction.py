# coding: utf-8

import tensorflow as tf
import fc_inference
import argparse
import csv
import numpy as np
from data_sets import DataSets, GFDataSet, PDataSet
import pdb
from sklearn.preprocessing import MinMaxScaler

INPUT_NODE = 4 * 4

FLAGS = None

class Prediciton(object):
    def prediction(self, data_sets, time_step):
        x = tf.placeholder(dtype=tf.float32, shape=[None,time_step, INPUT_NODE])
        y = tf.placeholder(dtype=tf.float32, shape=[None, time_step, fc_inference.n_target])

        reshape_x = tf.reshape(x,[-1, INPUT_NODE])
        y_ = fc_inference.chg_inference(reshape_x, None, None, False)

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
    
    def prediction_price(self, data_set_x,time_step):
        x = tf.placeholder(dtype=tf.float32, shape=[None,time_step, INPUT_NODE])
        reshape_x = tf.reshape(x,[-1, INPUT_NODE])
        y_ = fc_inference.chg_inference(reshape_x, None, None, False)

        saver = tf.train.Saver(tf.global_variables())
        with tf.Session() as sess:
            tf.global_variables_initializer().run()
            model_file = tf.train.latest_checkpoint('/kywk/strategy/model/close_price_4/model/')
            saver.restore(sess, model_file)
            out = sess.run([y_], feed_dict={x: data_set_x[0:1]})
            return out
    
    def signal(self, data_set):
        mean_data = np.mean(data_set, axis=0)
        std_data = np.std(data_set, axis=0)
        normalized_data = (data_set - mean_data) / std_data
        scaler = MinMaxScaler()
        scaler.fit(normalized_data)
        normalized_data = scaler.transform(normalized_data)
        input_data = normalized_data[0:4,].reshape(-1,16)
        input_data_x = []
        input_data_x.append(input_data)
        out = self.prediction_price(input_data_x,1)
        pred_price = np.squeeze(np.array(out[0:1])) * std_data[0] + mean_data[0]
        # return pred_price  - np.squeeze(data_set[4:,0:1])
        return pred_price
def main(argv=None):
    # data_set = np.array([[3300,3301,3298,3301],[3297,3300,3296,3299],[3297,3299,3296,3297],[3295,3298,3294,3297]])
    # data_set = np.array([[3286,3286,3275,3276],[3281,3286,3280,3285],[3283,3291,3280,3281],[3281,3286,3279,3283],[3285,3287,3280,3281]])
    # data_set = np.array([[3280,3281,3280,3281],[3281,3281,3280,3281],[3280,3281,3280,3281],[3282,3283,3280,3280],[3282,3283,3282,3282]])
    # pred = Prediciton()
    # print pred.signal(data_set)
    
    # t = np.squeeze(x_t)
    # data_sets = DataSets()
    # data_sets.gf_etf('./data/temp')
    # while data_sets.is_range():
    #    data_set = data_sets.train_batch()
    #    pred = Prediciton()
    #    mse_final = pred.prediction(data_set, data_set.test_step())
    #    print mse_final

    parser = argparse.ArgumentParser()
    parser.add_argument('--dir',type=str,help = 'data dir')
    FLAGS, unparsed = parser.parse_known_args()
    data_set = PDataSet()
    # data_set.calc_etf('./data/temp/ag1706_20161220.csv')
    data_set.calc_etf(FLAGS.dir)
    pred = Prediciton()
    loss = pred.prediction(data_set,data_set.test_step())
    print loss
    with open("./result/prediction.csv","aw") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows([[loss,FLAGS.dir]])

if __name__ == '__main__':
    tf.app.run()
