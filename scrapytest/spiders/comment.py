import logging
import threading

from scrapytest.spiders.getcommentpostdata import GetPostData
from scrapy.spiders import Spider
from scrapy.http import FormRequest, Request


class CommentSpider(Spider):
    name = 'comment'
    allowed_domains = ['music.163.com']
    song_id = ['27406244', '419837239']
    logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG)
    comment_url = 'http://music.163.com/weapi/v1/resource/commen' \
                     'ts/R_SO_4_{0}?csrf_token='
    lock = threading.Lock()

    def start_requests(self):
        # start_urls = 'https://httpbin.org/get'
        # yield Request(start_urls, meta={'lock': self.lock})
        request_list = []

        for id in self.song_id:
            start_urls = self.comment_url.format(id)
            data = GetPostData(songid=id).get_post_data()
            request_list.append(FormRequest(start_urls, formdata=data))
        return request_list

    def parse(self, response):
        # print(response.meta['test'])
        print(response.text)
