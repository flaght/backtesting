# coding: utf-8
from javis_data import JavisData
import pdb
import argparse


FLAGS = None


class StrangeEngine(object):
    def __init__(self):
        self.__javis_data = JavisData()

    def create_javis(self, uid, token):
        self.__javis_data.create_javis(uid, token)

    def build_dominat(self, path, filename):
        self.__javis_data.calut_dominant(path, filename)

    def build_dominat_bar(self, filename, out_dir):
        self.__javis_data.build_domiant_bar(filename, out_dir)

    def check_data(self, dir):
        self.__javis_data.check_data_dir(dir)

    def check_data_file(self, filename):
        self.__javis_data.check_data_file(filename)

if __name__ == '__main__':
    parsed = None
    parser = argparse.ArgumentParser()
    parser.add_argument('--type', type=int)
    parser.add_argument('--check_dir', type=str)
    parser.add_argument('--check_file', type=str)
    parser.add_argument('--dominat_file', type=str)
    parser.add_argument('--out_dir', type=str)
    FLAGS, _ = parser.parse_known_args()
    if FLAGS.type == None:
        print "2.指定文件将tick转化为bar数据\n3.构造主力合约的bar数据4.检查指定目录下数据是否正常(价格异常)\n5.检查指定文件的数据是否正常(价格异常)\n6.计算一年主力合约的合约列表\n7.请求合约tick数据"
    else:
        clt = JavisData()
        if FLAGS.type == 2:
            clt.tick_to_bar(FLAGS.check_dir,FLAGS.out_dir)
        elif FLAGS.type == 3:
            clt.build_dominat_bar(FLAGS.dominat_file, FLAGS.out_dir)
        elif FLAGS.type == 4:
            clt.check_data_dir(FLAGS.check_dir)
        elif FLAGS.type == 5:
            clt.check_data_file(FLAGS.check_file)
        elif FLAGS.type == 6:
            clt.calc_dominant(FLAGS.check_dir,FLAGS.dominat_file)
        elif FLAGS.type == 7:
            uid = 142
            token = 'adc28ac69625652b46d5c00b'
            clt = JavisData()
            clt.create_javis(uid, token)
            key_dict = [
                {'symbol':'ag0001.SHFE','start_time':'2017-1-3 9:00:00','end_time':'2017-1-29 15:00:00'}
            ]
            
            for key in key_dict:
                print key['symbol'], key['start_time'], key['end_time']
                print clt.send_data_pd(key['symbol'], key['start_time'], key['end_time'])
                print "==>"
