# coding: utf-8
import numpy as np
import pandas as pd
import os
import commands
import pdb
if __name__ == '__main__':
    np.set_printoptions(threshold=np.inf)
    #output_list = []
    for path, dirs, fs in os.walk('./data/out_dir/ag/ag2017/'):
        for f in fs:
            str = 'python fc_prediction.py --dir=' +  os.path.join(path, f)
            (status,output) = commands.getstatusoutput(str)
    #print output_list
    data = pd.read_csv('./result/prediction.csv').iloc[:,0:1]
    data = data.values
    print np.mean(data)
