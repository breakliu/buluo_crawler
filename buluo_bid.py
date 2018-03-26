# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests
# from bs4 import BeautifulSoup
from random import Random

config_bids = "bids.json"

# 把时间戳转成字符串形式
def timestamp_toString(stamp):
    return time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(stamp))

# 随机数字字符串生成
def random_string(randomlength=8, zero=False):
    chars = '0123456789'
    length = len(chars)-1
    random = Random()
    str = ''

    if zero:
        randomlength-=1
        str = chars[random.randint(1,length)]

    for i in range(randomlength):
        str+=chars[random.randint(0,length)]

    return str

# 生成URL
def get_url(bid, start=0):
    url='https://buluo.qq.com/cgi-bin/bar/post/get_post_by_page?bid='+bid+'&num=20&start='+str(start)+'&source=2&r=0.1'+random_string(17)+'&bkn='
    print(url)
    return url

# 生成头
def get_headers(bid):
    return {
        'content-type':'application/json;charset=utf-8',
        'accept':'application/json',
        'accept-language':'zh-CN,zh;q=0.8',
        'Referer':'https://buluo.qq.com/p/barindex.html?bid='+bid,
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
        'x-requested-with':'XMLHttpRequest'
    }

def get_total(bid, headers):
    url = get_url(bid)

    req = requests.request('GET', url, headers=headers)
    arr = json.loads(req.text)

    if arr['retcode'] != 0:
        print('This is bid[%s] get fail.' % bid)
        return False

    if 'total' not in arr['result']:
        print('bid[%s] can not get total.'%bid)
        return False

    return arr['result']['total']

def download(url, file_name):
    with open(file_name, "wb") as file:
        response = requests.get(url)
        file.write(response.content)

def fetch_images(post):
    path = os.path.join(os.getcwd(), 'data', str(post['bid']), str(post['pid']))
    idx = 1

    if False == make_path(path):
        print('%s exists' % path)
        return

    if 'post' in post and 'pic_list' in post['post']:
        for pic in post['post']['pic_list']:
            if 'url' in pic:
                # print(pic['url'])
                download(pic['url'], os.path.join(path, str(idx) + '.jpg'))
                idx += 1


# 获取发帖
def get_posts(bid, loop=None):
    try:
        headers = get_headers(bid)

        total = get_total(bid, headers)
        if total == False:
            return

        # 获取所有post
        for i in range(0, total, 20):
            url = get_url(bid, i)
            req = requests.request('GET', url, headers=headers)
            arr = json.loads(req.text)

            if arr['result'] and 'posts' in arr['result']:
                for post in arr['result']['posts']:
                    fetch_images(post)

            # time.sleep(1)

    except Exception as ex:
        print('bid[%] getposts error:%s' % (bid, ex))

def make_path(path):
    if os.access(path, os.R_OK):
        return False

    os.mkdir(path)
    return True

def main():
    make_path(os.path.join(os.getcwd(), 'data'))

    arr_bids = []
    with open(os.path.join(os.getcwd(), config_bids), "r") as file:
        arr_bids = json.load(file)

    for bid in arr_bids['bids']:
        make_path(os.path.join(os.getcwd(), 'data', bid))
        get_posts(bid)

if __name__ == '__main__':
    main()
