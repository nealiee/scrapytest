import json
import logging
import random
import string
import threading
import time
from queue import Queue

import requests
from scrapytest.util.sqloperationsqlite3 import DataBase
from scrapytest.util.ippool import DBOperation
# class MyThread(threading.Thread):
#     def __init__(self, queue, i):
#         threading.Thread.__init__(self)
#         self.i = i
#         self.queue = queue
#
#     def run(self):
#         t = threading.get_ident()
#         print('{} start {}'.format(t, time.ctime()))
#         time.sleep(self.i)
#         print('{} end {}'.format(t, time.ctime()))
#         self.queue.put('a')
#
#
# queue = Queue()
# for _ in range(5):
#     queue.put('a')
# for i in range(20):
#     queue.get()
#     MyThread(queue, i).start()



for i in string.ascii_uppercase:
    print(ord(i))

# def test(a, b, i='a', *c, **d):
#     print('a= ', a)
#     print('b= ', b)
#     print('i= ', i)
#     print('c= ', c)
#     print('d= ', d)
# f = ['xxx', 'yyy', 'ggg', 'iii']
# g = {'qwe': 123, 'asd': 321}
# test(*f, **g)