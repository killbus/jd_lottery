#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request, http.cookiejar
import re, random
import time
import json
import codecs
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def load_html(url):
	while True:
		try:
			cj=http.cookiejar.MozillaCookieJar()
			#cj.load(user,ignore_expires=True,ignore_discard=True)
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
			urllib.request.install_opener(opener)
			headers={'Host':'www.jd.com',
			'User-Agent':'Mozilla/5.0(WindowsNT6.3;WOW64;rv:47.0)Gecko/20100101Firefox/47.0',
			'Accept':'application/json,text/javascript,*/*;q=0.01',
			'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
			'X-Requested-With':'XMLHttpRequest',
			'Referer':'http://www.jd.com',
			'Connection':'keep-alive'}
			req=urllib.request.Request(url,headers=headers)
			response=opener.open(req, timeout=6)
			page=response.read().decode('utf-8', 'ignore')
			break
		except Exception as e:	
			print(time.ctime())
			print("无法下载网页。1秒后重试...")
			time.sleep(1)
			pass
	return page
		
result=[]
for p in range(1,6,1):
	url = "https://www.jd.com/queryNews.html?type=2&title=&page="+str(p)+"&r="+str(random.random())
	time.sleep(1)
	data = json.loads(load_html(url))
	for item in data['record']:
		print('目标：'+item['url'])
		url_tunple = urlparse(item['url'])
		if url_tunple.netloc != 'sale.jd.com':
			print('类型：文章')
			page = load_html('https://www.jd.com/'+item['url'])
			soup = BeautifulSoup(page, 'lxml')
			detail = soup.find(id='detail').find(class_='mc').get_text()
			act = re.search("sale\.jd\.com\/.*?\.html", detail)
			if act is not None:
				act = act.group()
				if urlparse(act).scheme not in ['http', 'https']:
					act = 'https://'+re.sub(r'(?i)^\/\/', '', act)
		else:
			act = item['url']
			print('类型：活动链接')
			if urlparse(act).scheme not in ['http', 'https']:
				act = 'https://'+re.sub(r'(?i)^\/\/', '', act)
		
		if act is not None and act not in result:
			result.append(act)
			print('结果：'+act)
		else:
			print('结果：没有找到有效的活动链接')
			
		print('-'*50)
			
if len(result) > 0:
	with codecs.open('acts.txt', 'w', 'utf-8') as a:
		for item in result:
			a.write(item+'\n')