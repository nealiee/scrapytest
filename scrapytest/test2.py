import time, threading
import random


def light():
    if not event.isSet():
        event.set()    #初始化绿灯, 设置为True, 非阻塞
    count = 0
    while 1:
        if count < 10:
            print('\033[1;32m ---green light on--- \033[0m')
        elif count < 13:
            print('\033[1;33m ---yellow light on--- \033[0m')
        elif count < 20:
            print('\033[1;31m ---red light on--- \033[0m')
            if event.isSet():
                event.clear()       #设置红灯, 阻塞
        else:
            count = 0
            event.set()   #绿灯
        time.sleep(1)
        count += 1


def car(n):
    while 1:
        time.sleep(random.randrange(2, 4))
        if event.isSet():
            print("car [%s] is running..." % n)
        else:
            print('car [%s] is waiting for the red light...' % n)
            event.wait()  # 红灯状态下调用wait方法阻塞，汽车等待状态


car_list = ['BMW', 'BEN', 'AUDI', 'SANTANA']
event = threading.Event()
l = threading.Thread(target=light)
l.start()
for i in car_list:
    t = threading.Thread(target=car, args=(i,))
    t.start()