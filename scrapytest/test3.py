import random
import threading, time
from queue import Queue

import os

import shutil


class MyThread(threading.Thread):
    def __init__(self, queue, lock):
        threading.Thread.__init__(self)
        self.queue = queue
        self.lock = lock

    def run(self):
        t = self.getName()
        print(t)
        while 1:
            with self.lock:
                file = self.queue.get()
            print(t, file)
            # time.sleep(random.randrange(1, 5))


def get_data(queue):
    while 1:
        for file in [i for i in os.listdir('.') if i.endswith('.gif')]:
            queue.put(file)
            filepath = os.path.join(tmp, file)
            if os.path.exists(filepath):
                os.remove(filepath)
            shutil.move(file, tmp)
        time.sleep(5)

threads = []
tmp = r'C:\Users\Administrator\Desktop\python\workspace\scrapytest\scrapytest\tmp'
lock = threading.Lock()
queue = Queue()

for i in range(5):
    threads.append(MyThread(queue, lock))

for t in threads:
    t.start()

get_data(queue)


