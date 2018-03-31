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
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
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
