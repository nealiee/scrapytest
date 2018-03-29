import random
import threading
import time


class Test(object):
    def __init__(self, name):
        self.name = name

    def p(self):
        print('test')
        time.sleep(random.randrange(1, 5))
        print(self.name)


t1 = Test('a')
t2 = Test('b')

p1 = threading.Thread(target=t1.p)
p2 = threading.Thread(target=t2.p)
p1.start()
p2.start()