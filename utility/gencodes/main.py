#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import os,sys
import signal
import codecs,random
import time, datetime
import urllib.request
from urllib.parse import urlparse
import chardet
from bs4 import BeautifulSoup

try:
    from http.cookiejar import CookieJar
except ImportError:
    from cookielib import CookieJar

class MyHTTPRedirectHandler(urllib.request.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        #print(cookieprocessor.cookiejar)
        result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        result.status = code
        return result
        #return urllib.request.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)

    http_error_301 = http_error_303 = http_error_307 = http_error_302

def get_userdata(file_url, dlist=False):
    data=[]
    with open(file_url,'r') as f1:
        flists=f1.readlines()
        if dlist:
            globals()[dlist] = flists
        for flist in flists:
            if flist[-1]=='\n':
                flist=flist[0:-1]
            if flist.strip() and (flist[0] != '#'):
                data.append(flist)
        data=tuple(data)
        return data

urls=get_userdata('urls.txt', 'urls_parent')

def extract(text, sub1, sub2):
    """
    extract a substring from text between first
    occurances of substrings sub1 and sub2
    """
    charset = text.split(sub1, 1)[-1].split(sub2, 1)[0]
    return charset if charset in ['utf-8', 'utf8', 'gbk', 'gb2312', 'gb18030'] else None
    
def load_html(url):
    while True:
        try:
            cj = CookieJar()
            opener = urllib.request.build_opener(MyHTTPRedirectHandler, urllib.request.HTTPCookieProcessor(cj))
            urllib.request.install_opener(opener)
            #req=urllib.request.Request(url, headers=headers)            
            #page=urllib.request.urlopen(req)
            opener.addheaders = [('Accept', '*/*'), ('Connection', 'keep-alive'), ('Host', 'item.m.jd.com'), ('Referer', 'http://www.jd.com'), ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')]
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
   
argv0_list = sys.argv[0].split("\\")
script_name = argv0_list[len(argv0_list) - 1]
script_name = script_name[0:-3]
tmp_record = script_name+'@'+str(os.getpid())+'.txt'

try:
    for url in urls:
        content = load_html(url)
        #encoding = extract(str(content).lower(), 'charset=', '"')
        encoding = chardet.detect(content)['encoding']
        #print('-'*50)
        #print( "Encoding type = %s" % encoding )
        #print('-'*50)
        if encoding:
        # note that Python3 does not read the html code as string
        # but as html code bytearray, convert to string with
            content = content.decode(encoding, 'ignore').replace(u'\xa9', u'')
        else:
            print("Debug: Encoding type not found!")
        match = re.search("\'(\w{8,}-\w{4,}-\w{4,}-\w{4,}-\w{12,})\'", str(content))
        if match is None and urlparse(url).path.startswith('/m/'):
            try:
                from selenium import webdriver
                dcap = dict(webdriver.DesiredCapabilities.PHANTOMJS)
                dcap["phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.98 Safari/537.36"
                dcap["phantomjs.page.settings.clearMemoryCaches"] = True
                dcap["phantomjs.page.customHeaders.accept"] = "*/*"
                dcap["phantomjs.page.customHeaders.Accept-Language"] = "en-US,en;q=0.7,zh;q=0.3"
                dcap["phantomjs.page.customHeaders.connection"] = "keep-alive"

                browser = webdriver.PhantomJS('phantomjs', desired_capabilities=dcap)
                browser.set_page_load_timeout(30)
                
                browser.get(url)
                browser.execute_script("var q = document.body.scrollTop = $('div[module-name=\"m-lottery\"]')[0].offsetTop")
                time.sleep(3)
                content = browser.page_source
                match = re.search("\'(\w{8,}-\w{4,}-\w{4,}-\w{4,}-\w{12,})\'", content)
            except Exception as e:
                print(e)
                
        if match is not None:
            soup = BeautifulSoup(content, 'lxml')
            title = ' '.join(' '.join(soup.title.string.split('-')[0:-1]).strip().split())
            code = match.group(1)
            #url_w = "http://ls-activity.jd.com/lotteryApi/getWinnerList.action?lotteryCode="+code+"&_=%d&callback="%(int(time.time()*1000))
            #winner = load_html(url_w)
            #winner = json.loads(str(load_html(url_w), 'utf-8'))
            #if 'data' in winner.keys() and len(winner['data']) > 0:
            #    winner = winner['data']
            #    awards = list(set([i['prizeName'] for i in winner]))
            #    awards = ', '.join(random.sample(awards, random.randint(1, len(awards) if len(awards) < 3 else 3)))
            #    desc = awards+' - '+title
            #    with codecs.open(tmp_record, 'a+', 'utf-8') as record:
            #        record.write(code+'\n; '+url+' '+desc+'\n')
            #else:
            #    awards = '没有中奖记录'
            
            url_i = "http://ls-activity.jd.com/lotteryApi/getLotteryInfo.action?callback=&lotteryCode=%s&_=%d"%(code, int(time.time()*1000))
            prize = json.loads(str(load_html(url_i), 'utf-8'))
            if 'data' in prize.keys() and prize['data'] is not None and len(prize['data']) > 0:
                prize = prize['data']
                etime = time.strptime(str(prize['endTime']),'%Y-%m-%d %H:%M:%S')
                etime=datetime.datetime(etime[0],etime[1],etime[2],etime[3],etime[4],etime[5])
                awards = list(set([i['prizeName'] for i in prize['lotteryPrize']]))
                awards = '，'.join(awards)
                desc = awards+' - '+prize['lotteryName']
                if (datetime.datetime.now() - etime).days <= 0:
                    vtime = prize['beginTime']+' - '+prize['endTime']
                    with codecs.open(tmp_record, 'a+', 'utf-8') as record:
                        record.write(code+'\n; '+url+' '+desc+'\n')
                else:
                    vtime = "已过期"
            else:
                print('-'*50)
                print('抽奖代码：'+code)
                print('错误信息：' +str(prize))
                print('链接地址：'+url)
                continue
            print('-'*50)
            print('抽奖代码：'+code)
            print('奖品举例：'+awards)
            print('活动时间：'+vtime)
        else:
            print('-'*50)
            print('错误信息：没有找到抽奖代码，请检查链接。')
            print('链接地址：'+url)

    try:
        browser.service.process.send_signal(signal.SIGTERM)
        browser.quit()
    except Exception as e:
        print(e)
        
    seen = set()
    with codecs.open('record.txt', 'w', 'utf-8') as record:
        with codecs.open(tmp_record, 'r', 'utf-8') as trecord:
            for line in trecord:
                if line not in seen and not line.startswith(';'):
                    record.write(line+next(trecord))
                    seen.add(line)
except Exception as e:
    print(e)
finally:
    if os.path.isfile(tmp_record):
        os.remove(tmp_record)