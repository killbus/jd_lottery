#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import codecs
import urllib.request

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

class MyHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        #print(cookieprocessor.cookiejar)
        return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

def load_html(url):
    while True:
        try:
            cj = CookieJar()
            opener = urllib.request.build_opener(MyHTTPRedirectHandler, urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)
            #req=urllib.request.Request(url, headers=headers)            
            #page=urllib.request.urlopen(req)
            opener.addheaders = [('Accept', '*/*'), ('Connection', 'keep-alive'), ('Host', urllib.parse.urlparse(url).netloc), ('Referer', 'http://'+urllib.parse.urlparse(url).netloc), ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
            page=urllib.request.urlopen(url, timeout=30)
            break
            #print(page.getcode())
        except Exception as e:
            print(str(e))
            print(time.ctime())
            print("无法下载网页。1秒后重试...")
            time.sleep(1)
    html=page.read()
    page.close()
    return html
    
with codecs.open('short.txt', 'w', 'utf-8') as record:
    with codecs.open('record.txt', 'r', 'utf-8') as trecord:
        for line in trecord:
            if not line.startswith(';'):
                curr_data = next(trecord).split(' ', 2)
                url = curr_data[1]
                desc = curr_data[2]
                url = load_html('http://z.gaozhouba.com/app/index.php?i=3&c=entry&do=ServicePromotionGetcode&m=jd_cun&materialId='+url).decode('utf-8', 'ignore')
                url = 'http://api.weibo.com/2/short_url/shorten.json?source=2849184197&url_long='+urllib.parse.quote_plus(url)
                res = json.loads(str(load_html(url).decode('utf-8', 'ignore')))
                short_url = res['urls'][0]['url_short']
                print(short_url)
                record.write(line+'; '+short_url+' '+desc)