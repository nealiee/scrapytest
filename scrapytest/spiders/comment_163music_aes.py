import base64
import csv
import json

import math
import re

import requests
from bs4 import BeautifulSoup
from Cryptodome.Cipher import AES

# url = 'http://music.163.com/song?id=539941039'

header = {
        'Host': 'music.163.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Accept-Encoding': 'gzip, deflate',
        'Referer': 'http://music.163.com/',
        'Cookie': '__e_=1515762580802; _ntes_nnid=bd322c1914301b03c620d050c8392491,1515762609162; '
                  '_ntes_nuid=bd322c1914301b03c620d050c8392491; usertrack=ezq0plpcOW+p7wfpBT9FAg==; _ga=GA1.2.1654812800.1515993505; JSESSIONID-WYYY=QfrnpvBje07fy%2BdT8WsywN2dKTWxKHVRfYc9Ie57FG4ocyUrbJcqeeVRuz4%5Ch0DUqWGnsDujmE29nduA4yJ%2ByHtmYlVuY8tPP9S10A9AlHCMkXwONukVGkWQQoUg2bQH3CHzQq%5CFvS%5CP%2B%2BpAv%5CNzG2kf%2FftKCXJ4DoD7KkY%5CaZJ3pEZT%3A1520475417516; _iuqxldmzr_=32; __utma=94650624.1654812800.1515993505.1520473618.1520473618.1; __utmb=94650624.35.8.1520474805729; __utmc=94650624; __utmz=94650624.1520473618.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
        'Connection': 'keep-alive'
    }



def get_params(first_param, forth_param):
    iv = b'0102030405060708'
    first_key = forth_param
    second_key = b'F' * 16
    encText = AES_encrypt(first_param, first_key, iv)
    encText = AES_encrypt(encText, second_key, iv)
    return encText

def get_encSecKey():
    encSecKey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
    return encSecKey


def AES_encrypt(text, key, iv):
    #确保是16的倍数
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text.encode())
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text.decode()


def get_comment_dict(song_id, offset=0):
    first_param = '{"rid":"R_SO_4_%s","offset":"%s","total":"true","limit":"20",' \
                  '"csrf_token":""}' % (song_id, offset)
    second_param = '010001'
    third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629' \
                  'ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b42' \
                  '4d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    forth_param = b'0CoJUm6Qyw8W8jud'
    comment_url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{0}?csrf_token='.format(song_id)

    params = get_params(first_param, forth_param)
    encSecKey = get_encSecKey()

    data = {
        'params': params,
        'encSecKey': encSecKey
    }

    response = requests.post(comment_url, headers=header, data=data)
    return json.loads(response.text)


def get_song_info(song_id):
    url = 'http://music.163.com/song?id={}'.format(song_id)
    response = requests.get(url, headers=header)
    bsObj = BeautifulSoup(response.text, 'lxml')
    return {
        'title': bsObj.find('em', class_='f-ff2').text,
        'singer': bsObj.find('p', class_='des s-fc4').a.text
    }



def main(song_id):
    info = get_song_info(song_id)
    total = get_comment_dict(song_id)['total']
    loop_count = math.ceil(total/20)
    emoji_pattern = re.compile(u'[\U00010000-\U0010ffff]')
    with open('{}.csv'.format(info['title']), 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([info['title'], info['singer'], total])
        writer.writerow(['用户id', '用户名', '评论', '赞', '时间', '评论id'])
        for i in range(int(loop_count)):
            comments = get_comment_dict(song_id, i*20)['comments']
            for comment in comments:
                print([comment['user']['userId'],
                                 re.sub(emoji_pattern, '[emoji]', comment['content']),
                                 comment['likedCount'],
                                 comment['commentId']])
                # try:
                #     writer.writerow([comment['user']['userId'],
                #                      comment['user']['nickname'],
                #                      re.sub(emoji_pattern, '[emoji]', comment['content']),
                #                      comment['likedCount'],
                #                      comment['time'],
                #                      comment['commentId']]
                #                     )
                # except Exception:
                #     pass




if __name__ == '__main__':
    # song_id = '29717271'
    # first_param = '{"rid":"R_SO_4_' + song_id + '","offset":"0","total":"true","limit":"20","csrf_token":""}'
    # second_param = '010001'
    # third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
    # forth_param = b'0CoJUm6Qyw8W8jud'
    # url = 'http://music.163.com/weapi/v1/resource/comments/R_SO_4_{0}?csrf_token='.format(song_id)
    main(27406244)
