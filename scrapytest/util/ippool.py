import json
import re
import threading
from pprint import pprint
from queue import Queue
from urllib.parse import urljoin
from time import sleep

import os
import requests
from PIL import Image
from bs4 import BeautifulSoup
from pytesseract import pytesseract

from scrapytest.util.setting import *
from scrapytest.util.sqloperationsqlite3 import DataBase


class SaveIpThread(threading.Thread):
    def __init__(self, func):
        threading.Thread.__init__(self)
        self.func = func

    def run(self):
        while 1:
            threads = []
            iplist = func()
            for ipinfo in iplist:
                threads.append(VerifyUrlAndSave(ipinfo))
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            print('DONE')
            lock.acquire()
            DBOperation().del_invalidip()
            lock.release()
            sleep(300)


class VerifyUrlAndSave(threading.Thread):
    def __init__(self, ipinfo):
        threading.Thread.__init__(self)
        self.ipinfo = ipinfo

    def run(self):
        num.acquire()
        ip, type = self.ipinfo
        if DBOperation(ip=ip, type=type)._sel():
            if type == 'http':
                verify_url = HTTP_VERIFY_URL
            else:
                verify_url = HTTPS_VERIFY_URL
            try:
                response = requests.get(verify_url, headers=HEADER, proxies={type: ip}, timeout=10)
                if response.status_code == 200:
                    ip1 = re.search(r'.*://(.*):.*', ip).group(1)
                    ip2 = ''
                    text = json.loads(response.text)
                    if 'origin' in text.keys():
                        ip2 = text['origin']
                    if ip1 == ip2:
                        response1 = requests.get(POINT_URL, headers=HEADER, proxies={type: ip}, timeout=15)
                        if response1.status_code == 200:
                            lock.acquire()
                            DBOperation(ip=ip, type=type)._save()
                            lock.release()
            except Exception as e:
                pass
        else:
            print(ip + '已存在')
        num.release()


class DBOperation(object):
    def __init__(self, ip='', type='', lock=threading.Lock()):
        self.ip = ip
        self.type = type
        self.lock = lock

    def _save(self):
        db = DataBase()
        if self._sel():
            sql = "insert into ip_pool(ip, type, insert_time, valid, err_time) \
                          values ('%s', '%s', datetime('now', 'localtime'), 'Y',0)" % (self.ip, self.type)
            if not db.idu(sql):
                print('{}保存失败'.format(self.ip))
        db.close()

    def _sel(self):
        db = DataBase()
        sql = "select * from ip_pool where ip='%s' and type='%s'" % (self.ip, self.type)
        res = db.fetch_all(sql)
        db.close()
        if res:
            return False
        return True

    def del_invalidip(self):
        db = DataBase()
        sql = "delete from ip_pool where err_time>=2 and insert_time<datetime('now', '-1 hour', 'localtime')"
        db.idu(sql)
        db.close()

    def select_validiplist(self):
        db = DataBase()
        sql = "select ip from ip_pool where err_time<2 and type='%s'" % (self.type,)
        res = db.fetch_all(sql)
        db.close()
        return [i[0] for i in res]

    def update_errtime(self):
        db = DataBase()
        sql = "update ip_pool set err_time=err_time+1 where ip='%s'" % (self.ip,)
        self.lock.acquire()
        db.idu(sql)
        self.lock.release()
        db.close()


def get_iplist_from_mimvp():
    try:
        response = requests.get(MIMVP_HPURL, headers=HEADER)
        if response.status_code != 200:
            return []
    except Exception as e:
        return []
    page_text = response.text
    ip_list = re.findall(r"<td class='tbl-proxy-ip' style='text-align: left;'>(\d+?\.\d+?\.\d+?\.\d+?)</td>",
                         str(page_text))
    port_list = re.findall(r"<img src=(common/ygrandimg.php\?id=\d+?&port=\w+) />",
                           str(page_text))
    type_list = re.findall(r"<td class='tbl-proxy-type' style='text-align: "
                           r"center;white-space:nowrap;overflow:hidden;' title='(HTTP|HTTPS|HTTP/HTTPS)'",
                           str(page_text))
    iplist = []
    for info in list(zip(ip_list, port_list, type_list)):
        ip = info[0]
        port_imgurl = urljoin(MIMVP_BASH_URL, info[1])
        type = info[2]
        img_id = re.search(r'.*port=(\w+)', port_imgurl).group(1)
        imgfilename = '{}.jpg'.format(img_id)
        imgconvertfilename = '{}_conv.jpg'.format(img_id)
        try:
            response = requests.get(port_imgurl, headers=HEADER)
            if response.status_code != 200:
                continue
        except Exception as e:
            continue
        with open(imgfilename, 'wb') as f:
            f.write(response.content)
        if os.path.exists(imgfilename):
            img = Image.open(imgfilename).convert('RGB')
            img = img.resize((img.size[0] * 4, img.size[1] * 4), Image.ANTIALIAS)
            img.save(imgconvertfilename, quality=95)
            img = Image.open(imgconvertfilename)
            value = pytesseract.image_to_string(img, config='-psm 3')
            os.remove(imgfilename)
            os.remove(imgconvertfilename)
            for t in type.split('/'):
                iplist.append([t.lower() + '://' + ip + ':' + value, t.lower()])
    return iplist


def get_iplist_from_xici():
    iplist = []
    for i in range(1, 3):
        url = XICI_NNURL.format(i)
        try:
            response = requests.get(url, headers=HEADER)
            if response.status_code != 200:
                return []
        except Exception as e:
            return []
        bsObj = BeautifulSoup(response.text, 'lxml')
        ip_list = bsObj.find('table', id='ip_list')
        ip_list = re.findall(r'<td>(\d+?\.\d+?\.\d+?\.\d+?)</td>.<td>(\d+)</td>.*?<td>(HTTP|HTTPS)</td>', str(ip_list),
                             re.DOTALL)
        for i, j, k in ip_list:
            iplist.append([k.lower() + '://' + i + ':' + j, k.lower()])
    return iplist


if __name__ == '__main__':
    num = threading.BoundedSemaphore(10)
    lock = threading.Lock()
    funcs = [get_iplist_from_mimvp, get_iplist_from_xici]
    for func in funcs:
        SaveIpThread(func).start()
