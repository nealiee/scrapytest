import json
import random
from time import sleep

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapytest.settings import URL_TYPE
from scrapytest.util.ippool import DBOperation


class MyRandomUserAgentMiddleware(UserAgentMiddleware):
    def process_request(self, request, spider):
        ua = random.choice(self.ua_list)
        request.headers['Referer'] = 'http://music.163.com/'
        request.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,' \
                                    'image/webp,image/apng,*/*;q=0.8'
        if ua:
            request.headers['User-Agent'] = ua

    ua_list = [
        'Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) '
        'Chrome/18.0.1025.166 Safari/535.19',
        'Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, '
        'like Gecko) Version/4.0 Mobile Safari/534.30',
        'Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) '
        'Version/4.0 Mobile Safari/533.1',
        'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0',
        'Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0',
        'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 '
        'Safari/537.36',
        'Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) '
        'Chrome/18.0.1025.133 Mobile Safari/535.19',
        'Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 '
        'Mobile/9A334 Safari/7534.48.3',
        'Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 '
        'Mobile/3A101a Safari/419.3',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'
    ]


class MyRandomProxyMiddleware(HttpProxyMiddleware):
    iplist = []

    def process_request(self, request, spider):
        if 'change_proxy' in request.meta.keys():
            invalid_proxy = request.meta['proxy']
            print('无效代理' + invalid_proxy)
            del request.meta['change_proxy']
            DBOperation(ip=invalid_proxy).update_errtime()
            if invalid_proxy in self.iplist:
                self.iplist.remove(invalid_proxy)

        while not self.iplist:
            self.iplist = DBOperation(type=URL_TYPE).select_validiplist()
            sleep(5)
        request.meta['proxy'] = random.choice(self.iplist)
        # request.meta['proxy'] = 'https://118.114.77.47:8080'

    def process_response(self, request, response, spider):
        if response.status != 200:
            request.meta['change_proxy'] = True
            request.dont_filter = True
            return request
        try:
            jsonstr = json.loads(response.text)
            if 'msg' in jsonstr.keys():
                if jsonstr['msg'] == 'Cheating':
                    request.meta['change_proxy'] = True
                    request.dont_filter = True
                    return request
        except Exception:
            pass
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, Exception):
            print(exception)
            request.meta['change_proxy'] = True
            request.dont_filter = True
            return request
