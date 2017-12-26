# coding: utf-8
import tensorflow as tf


class Monitor(object):
    def __init__(self, dir):
        self.__dir = dir
        self.__summary_writer = None

    def __del__(self):
        if self.__summary_writer != None:
            self.__summary_writer.close()

    def variable_summaries(self, name, var):
        self.histogram(name, var)
        self.scalar('meam/' + name, tf.reduce_mean(var))
        self.scalar('stddev/' + name, tf.sqrt(tf.reduce_mean(tf.square(var - tf.reduce_mean(var)))))
    
    def histogram(self, name, var):
        tf.summary.histogram(name, var)

    def scalar(self, name, var):
        tf.summary.scalar(name, var)

    def merged(self):
        return tf.summary.merge_all()

    def create(self, graph):
        self.__summary_writer = tf.summary.FileWriter(self.__dir, graph)

    def writer(self, summary, i=0):
        self.__summary_writer.add_summary(summary, i)
