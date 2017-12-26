# -*- coding:utf-8 -*-
from socket import *
import struct
import hashlib
import sys
import time
import json
from mlog import MLog

# h_type = 4
# head = [0, 0, h_type, 0, 4003, 0, 3, 7, 6]


class Client(object):
    domain = '222.73.12.3'
    port = 16100

    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.connect((self.domain, self.port))
        self.list = []
        self.log = MLog(name="javis")

    def __del__(self):
        self.sock.close()

    def __send_message(self, sock, packBuf, total):
        i = total
        while i > 0:
            # print('i: %d' % i)
            sock.send(packBuf)
            time.sleep(1)
            recv_buff = sock.recv(8024000)
            # print recvBuff
            dynatick = json.loads(recv_buff)
            #unit_dynatick = dynatick.get('dt')
            next_time = dynatick.get('nt') 
            i -= 1
        return next_time

    def __send_file(self, sock, packBuf, total):
        sock.send(packBuf)
        time.sleep(1)
        recvBuff = sock.recv(8024000)
        #print recvBuff
        #http_info = json.loads(recvBuff)
        http_info = len(recvBuff)
        return http_info

    def __fill_packet(self, type, opecode, jsonStr):
        head = [0, 0, 4, 0, 0, 0, 3, 7, 6]
        head[2] = type
        head[4] = opecode
        head[5] = len(jsonStr)
        head[0] = 26 + head[5]
        head.append(jsonStr)
        headRes = tuple(head)
        fmt = 'h2b3hIqh{0}s'
        fmtRes = fmt.format(head[5])
        s = struct.Struct(fmtRes)
        packBuf = s.pack(*headRes)
        return packBuf
    
    def set_user(self, uid, token):
        self.uid = uid
        self.token = token
   
    def dyna_file(self, symbol, start_time, end_time):
        jsonStr = '"uid":{0}, "access_token":"{1}", "sec_id":"{2}","field":"json", "start_time":"{3}","end_time":"{4}"'  # 4003
        jsonStrRes = ('{' + jsonStr.format(self.uid, self.token, symbol, start_time, end_time) + '}').encode()
        packBuf = self.__fill_packet(4, 2003, jsonStrRes)
        return self.__send_file(self.sock, packBuf, 1)
    
    def dyna_tick(self, symbol, start_time, end_time):
        while True:
            jsonStr = '"uid":{0}, "access_token":"{1}", "sec_id":"{2}","field":"json", "start_time":"{3}","end_time":"{4}"'  # 4003
            jsonStrRes = ('{' + jsonStr.format(self.uid, self.token, symbol, start_time, end_time) + '}').encode()
            packBuf = self.__fill_packet(4, 2003, jsonStrRes)
            next_time = self.__send_message(self.sock, packBuf, 1)
            if (next_time == 0):
                break
            start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(next_time))
            self.log.log().debug("symbol %s: %s end_time:%s",symbol, start_time, end_time)
        return self.list

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf8')
    uid = 142
    token = 'adc28ac69625652b46d5c00b'
    symbol = "bu1709.SHFE"
    start_time = "2016-1-1 9:15:12"
    end_time = "2016-2-18 23:10:21"
    client = Client()
    client.set_user(uid,token)
    list = client.dyna_tick(symbol,start_time,end_time)
    # print len(list)
    # for i in list:
    #    print i


