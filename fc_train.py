# coding: utf-8

import tensorflow as tf
from data_sets import DataSets,PDataSet
from monitor import Monitor
import numpy as np
import os
import fc_inference

INPUT_NODE = 10 * 4
#n_target = 1
LEARNING_RATE_BASE = 0.0 
LEARNING_RATE_DECAY = 0.99

REGULARIZATION_RATE = 0.0001
MOVING_AVERAGE_DECAY = 0.99

MODEL_SAVE_PATH = './model/'
MODEL_NAME = 'model.ckpt'
SUMMARY_DIR = 'log/'


def train(data_sets, batch_size = 50, time_step = 55):
    f_monitor = Monitor(SUMMARY_DIR)
    x = tf.placeholder(dtype=tf.float32, shape=[None, time_step, INPUT_NODE])
    y = tf.placeholder(dtype=tf.float32, shape=[None, time_step, fc_inference.n_target])


    reshape_x = tf.reshape(x, [-1, INPUT_NODE])
    
    y_ = fc_inference.chg_inference(reshape_x, f_monitor, None, False)

    #存储训练轮数的变量
    global_step = tf.Variable(0, trainable=False)

    #variable_averages = tf.train.ExponentialMovingAverage(
    #    MOVING_AVERAGE_DECAY,global_step
    #    )

    #variable_averages_op = variable_averages.apply(
    #    tf.trainable_variables(
    #    ))
    
    cross_entropy_mean = tf.reduce_mean(tf.square(tf.reshape(y_,[-1])-tf.reshape(y, [-1])))
    #cross_entropy_mean = tf.reduce_mean(tf.squared_difference(y, y_))

    f_monitor.scalar('cross_entropy_mean', cross_entropy_mean)


    #regularizer = tf.contrib.layers.l2_regularizer(REGULARIZATION_RATE)

    #regular = fc_inference.chg_inference_regular(regularizer)

    #总损失为交叉熵和正则化损失的和
    #loss = cross_entropy_mean + regular
    loss = cross_entropy_mean
    f_monitor.scalar('loss', loss)

    #train_x, train_y = data_sets.train_batch()
    

    #learning_rate = tf.train.exponential_decay(LEARNING_RATE_BASE,
    #                                           global_step,
    #                                           len(train_x) * 2000,
    #                                           LEARNING_RATE_DECAY)

    train_step = tf.train.AdadeltaOptimizer(0.05).minimize(loss, global_step)

    #with tf.control_dependencies([train_step, variable_averages_op]):
    #    train_op = tf.no_op(name='train')

    saver = tf.train.Saver()

    merged = f_monitor.merged()

    with tf.Session() as sess:
        
        f_monitor.create(sess.graph)

        tf.global_variables_initializer().run()
        for i in range(100):
            while data_sets.is_range():
                data_set = data_sets.train_batch()
                print("filename %s" %(data_set.file_name()))
                batch_index, train_x, train_y = data_set.train_batch()
                for step in range(len(batch_index) - 1):
                    _,mse_final, summary, step_ = sess.run([train_step, loss, merged, global_step],
                                                       feed_dict={x:train_x[batch_index[step]: batch_index[step + 1]],
                                                                  y:train_y[batch_index[step]: batch_index[step + 1]]})
            f_monitor.writer(summary,step_)
            data_sets.reset()
            print("After %d train step(s), loss on training"
              " batch is %g" %(step_, mse_final))
            if i % 10 == 0:
                saver.save(sess,os.path.join(MODEL_SAVE_PATH, MODEL_NAME), global_step=step_)


def main(argv=None):
   # data_set = PDataSet()
   # data_set.calc_etf('./data/out_dir/ag1606_20160104.csv')
   # train(data_set, data_set.batch_size(),data_set.train_step())
   np.set_printoptions(threshold=np.inf)
   data_sets = DataSets()
   data_sets.gf_etf('./../fc/data/temp_train/')
   
   # while data_sets.is_range():
   #    data_set = data_sets.train_batch()
   #    print("filename %s" %(data_set.file_name()))
   #    batch_index, train_x, train_y = data_set.train_batch()
   #    print batch_index
   #    print '<------------------->'
   #    print train_x
   #    print '<------------------->'
   #    print train_y
   train(data_sets)

if __name__ == '__main__':
    tf.app.run()
