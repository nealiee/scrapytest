import logging
import re
import string
import threading

from scrapytest.spiders.getcommentpostdata import GetPostData
from scrapy.spiders import Spider
from scrapy.http import FormRequest, Request
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class CommentSpider(Spider):
    name = 'comment'
    allowed_domains = ['music.163.com']
    song_id = ['27406244', '419837239']
    logging.basicConfig(filename='test.log', filemode='w', level=logging.DEBUG)
    bash_url = 'http://music.163.com'
    comment_url = 'http://music.163.com/weapi/v1/resource/commen' \
                     'ts/R_SO_4_{0}?csrf_token='
    country_id = ['1001']
    # country_id = ['1001', '1002', '1003', '2001', '2002', '2003', '6001', '6002', '6003', '7001', '7002', '7003',
    #               '4001', '4002', '4003']
    all_artist_url = 'http://music.163.com/discover/artist/cat?id={}&initial={}'
    hot_artisl_url = 'http://music.163.com/discover/artist/cat?id={}&initial=-1'

    def start_requests(self):
        # start_urls = 'https://httpbin.org/get'
        # yield Request(start_urls, meta={'lock': self.lock})
        request_list = []

        for id in self.country_id:
            request_list.append(Request(self.hot_artisl_url.format(id,)))
            # for initial in string.ascii_uppercase:
            #     request_list.append(Request(self.all_artist_url.format(id, ord(initial))))
            # start_urls = self.comment_url.format(id)
            # data = GetPostData(songid=id).get_post_data()
            # request_list.append(FormRequest(start_urls, formdata=data))
        return request_list

    def parse(self, response):
        bsobj = BeautifulSoup(response.text, 'lxml')
        artist_list = bsobj.find_all(class_='nm nm-icn f-thide s-fc0', href=re.compile(r'^ ?/artist\?id=\d+$'))
        for artist in artist_list:
            url = self.bash_url + artist['href'].strip()
            artist_name = artist.get_text()
            artist_id = re.search(r'.*id=(\d+)', artist['href'].strip()).group(1)
            yield Request(url=url, meta={'artist_name': artist_name, 'artist_id': artist_id}, callback=self.artist_page)

    def artist_page(self, response):
        print(response.meta['artist_name'], response.meta['artist_id'])
