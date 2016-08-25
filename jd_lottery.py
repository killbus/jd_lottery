#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

import re
import time
import random

import smtplib
from email.mime.text import MIMEText

import configparser#read and save configuration.
import ast
import json

import sys
import webbrowser
import codecs

def beep():
    """play an alarm."""
    print("\a")

    """
    import winsound
    Freq = 500 # Set Frequency To 2500 Hertz
    Dur = 200 # Set Duration To 1000 ms == 1 second
    winsound.Beep(Freq,Dur)
    """

class Settings:
    """
    Read settings from jd_lottery.ini .
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config=configparser.ConfigParser(delimiters=('='), allow_no_value=True)
        with codecs.open('jd_lottery.ini', "r", "utf-8") as f:
            first = f.read(1)
            if first != "\ufeff":
                # not a BOM, rewind
                f.seek(0)
            self.config.read_file(f)

    def get_sleep_interval(self):
        """Get interval between every two waves of querying."""
        try:
            time_str=self.config.get("通用设置", "查询时间间隔秒")
            time_str_list=time_str.replace("x", "*").replace("X", "*").split("*")
            seconds=1
            for i in time_str_list:
                seconds=seconds*int(i)
            if seconds>0:
                return seconds
            else:
                return 60
        except Exception as e:
            print(str(e))
            return 60

    def get_MONITORING_CODE(self):
        try:
            MONITORING_CODE=self.config.get("通用设置", "监控抽奖代码")
            return MONITORING_CODE
        except Exception as e:
            print(str(e))
            return ""

    def is_debug(self):
        try:
            debug_str=self.config.get("通用设置", "调试")
            if debug_str in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False
    def is_play_music(self):
        try:
            is_query=self.config.get("变更播放提示音乐", "播放音乐")
            if is_query in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        

    def get_music_path(self):
        try:
            return self.config.get("变更播放提示音乐", "音乐位置")
        except Exception as e:
            print(str(e))
            return ""

    def is_send_email(self):
        try:
            is_send=self.config.get("邮件提醒", "发送邮件提醒")
            if is_send in ("True", "true", "TRUE", "是"):
                return True
            else:
                return False
        except Exception as e:
            print(str(e))
            return False        

    def get_sender_email_server(self):
        try:
            return self.config.get("邮件提醒", "发件人邮件服务器")
        except Exception as e:
            print(str(e))
            return ""
    def get_sender_email_account(self):
        try:
            return self.config.get("邮件提醒", "发件人邮箱账号")
        except Exception as e:
            print(str(e))
            return ""
    def get_sender_email_passwd(self):
        try:
            return self.config.get("邮件提醒", "发件人邮箱密码")
        except Exception as e:
            print(str(e))
            return ""

    def get_receiver_email_account(self):
        try:
            return self.config.get("邮件提醒", "收件人邮箱账号").split("|")
        except Exception as e:
            print(str(e))
            return ""

settings = Settings()
s=requests.session()

MAX_PRICE=10000000
#SLEEP_INTERVAL seconds.
SLEEP_INTERVAL=settings.get_sleep_interval()
MONITORING_CODE=settings.get_MONITORING_CODE()
DEBUG=settings.is_debug()

PLAY_MUSIC=settings.is_play_music()
MUSIC_PATH=settings.get_music_path()
SEND_EMAIL=settings.is_send_email()
SENDER_MAIL_SERVER=settings.get_sender_email_server()
SENDER_EMAIL_ACCOUNT=settings.get_sender_email_account()
SENDER_EMAIL_PASSWD=settings.get_sender_email_passwd()
RECEIVER_EMAIL_ACCOUNTS=settings.get_receiver_email_account()


class Product:
    def __init__(self,code_i):
        self.code_i=code_i
        self.url="http://ls-activity.jd.com/lotteryApi/getWinnerList.action?lotteryCode="+code_i+"&_=%d&callback="%(int(time.time()*1000))
        self.page=None
        self.html=None
        #self.load_html()

    def load_html(self):
        try:
            headers={'Host':'ls-activity.jd.com',
            'User-Agent':'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.76 Mobile Safari/537.36',
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
            'Referer':'http://m.jd.com/',
            'Connection':'keep-alive'}
            req=s.get(self.url,headers=headers)
            self.page=req.text
        except Exception as e:
            print(str(e))
            beep()
            print(time.ctime())
            print("无法下载网页。1秒后重试...")
            time.sleep(1)
            self.__init__(self.code_i)
            self.load_html()
            return None
        self.html=self.page
        return self.html

class Result:
    """
    Read/save goods info from/to jd_lottery_result.txt.
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config = configparser.RawConfigParser()
        self.config.read('jd_lottery_result.txt')
        
    def get_url(self, code):
        try:
            return self.config.get(code, 'url')
        except Exception as e:
            print(str(e))
            return ''
            
    def set_url(self, code, _str):
        string = str(_str)
        with open('jd_lottery_result.txt', 'w') as configfile:
            if not self.config.has_section(code): self.config.add_section(code)
            self.config.set(code, 'url', string)
            self.config.write(configfile)
            
    def get_data(self, code):
        try:
            return self.config.get(code, 'res')
        except Exception as e:
            print(str(e))
            return ''

    def set_data(self, code, _str):
        string = str(_str)
        with open('jd_lottery_result.txt', 'w') as configfile:
            if not self.config.has_section(code): self.config.add_section(code)
            self.config.set(code, 'res', string)
            self.config.write(configfile)
            
def internet_on():
    """Check if computer is online. Return type: boolean."""
    try:
        response=s.get("http://www.baidu.com",timeout=100)
        return True
    except Exception as e:
        print(str(e))
        return False

def send_mail(sub,content,to_list=RECEIVER_EMAIL_ACCOUNTS):
    mail_host=SENDER_MAIL_SERVER
    mail_user=SENDER_EMAIL_ACCOUNT #用户名
    mail_pass=SENDER_EMAIL_PASSWD #口令

    me=mail_user
    msg = MIMEText(content,_subtype='LOGIN',_charset='UTF-8')
    msg['Subject'] = sub
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    try:
        server = smtplib.SMTP()
        server.set_debuglevel(1)
        server.connect(mail_host, 587)
        server.starttls()
        server.login(mail_user,mail_pass)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        print("邮件发送成功！")
        return True
    except Exception as e:
        print(str(e))
        print("正在检查网络连接...")
        if True==internet_on():
            print("网络畅通，或许账号或密码有误。程序终止以避免频繁尝试登陆邮箱。")
            raise NameError("账号密码有误，请检查。")
        else:
            print("网络故障，稍后重试...")
            return False

def Run():

    #Counting querying times.
    count=0
    #JD goods id.
    CODE=re.findall(r"(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", MONITORING_CODE)
    CODE=list(set(CODE))
    while(True):
        #Format output
        with codecs.open('output.html', 'w', 'utf-8') as html:
            html.write(u'<!DOCTYPE html>\n<html>\n    <head>\n        <meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0"/>\n        <meta name="format-detection" content="telephone=no" />\n        <meta http-equiv="refresh" content="10">\n        <title>京东抽奖测水</title>\n    </head>\n    <body>\n')
            
        #Endless querying with sleep interval, until user quit the program.
        count+=1
        #Sum up all changes in a single query and print at the end of the prompt.
        change_print=""
        #Introduce randomness to simulate human clicking. Avoiding IP ban from jingdong.
        random.shuffle(CODE)
        #For each link setted in file.
        for code_i in CODE:
            time.sleep(random.randint(100,200)/1000)
            #http://ls-activity.jd.com/lotteryApi/getWinnerList.action?lotteryCode=e70e381a-29a9-4361-ba47-bce3b2e72348&_=1472104982912&callback=jsonp8
            url_i = "http://ls-activity.jd.com/lotteryApi/getWinnerList.action?lotteryCode="+code_i+"&_=%d&callback="%(int(time.time()*1000))
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++")

            product=Product(code_i)

            result=Result()
            prev_url=result.get_url(code_i)
            prev_data=result.get_data(code_i)
            news=False

            curr_data=product.load_html()

            #save url to file if url not saved:
            if prev_url!=url_i:
                result.set_url(code_i, url_i)

            ########################################################
            #data changed：
            if curr_data!=prev_data:
                news=True
                result.set_data(code_i, curr_data)

            #detection finished.
            ########################################################

            message = u"数据      ："+curr_data+"\n"+          \
                      u"网址      ："+url_i+"\n"

            if news:
                print("检测到变更！！！")
                data = json.loads(json.dumps(curr_data))
                if SEND_EMAIL:
                    #Try 10 times if unabled to send email.
                    for i in range(10):
                        if send_mail("%s%d%s"%(news_type,curr_price,curr_title), message):
                            news_type=""
                            break;
                        else:
                            beep()
                            print("无法发送。30秒后重试...")
                            time.sleep(30)

                if PLAY_MUSIC:
                    webbrowser.open(MUSIC_PATH)

            else:
                print("无变更。")
            print(message)

        print("##############################################################")
        #print out current time.
        print(time.ctime())
        print("第"+str(count)+"次 汇总结果：")
        if ""==change_print:
            print("无变更。")
        else:
            print(change_print)
            
        #Format output
        with codecs.open('output.html', 'a', 'utf-8') as html:
            html.write(u'\n    </body>\n</html>')
            
        #Randomness added to sleep interval, simulating human clicking and refreshing.
        RAND_INT = random.randint(-5,5)
        SLEEP_INTERVAL_RANDOM=int(SLEEP_INTERVAL+RAND_INT)
        if SLEEP_INTERVAL_RANDOM < 1:
            SLEEP_INTERVAL_RANDOM=1

        print("等待 %d+%d=%d秒 更新..."%(SLEEP_INTERVAL, RAND_INT, SLEEP_INTERVAL_RANDOM))
        print("如数字不跳动，请按ESC来退出选择模式。")
        #Countdown shown on the same position on prompt.
        count_length = len(str(SLEEP_INTERVAL_RANDOM))
        for i in range(SLEEP_INTERVAL_RANDOM,0,-1):
            sys.stdout.write(str(i)+" "+"\r")
            time.sleep(1)
            sys.stdout.flush()
            
        print("正在获取网页...\n\n")




if __name__ == '__main__':
    while True:
        try:
            Run()
        except Exception as e:
            print(e)
            beep()
            time.sleep(5)


'''
#Price: another way to obtain
import requests
pids=1217524
url="http://p.3.cn/prices/mgets?skuIds=J_1217524"# + str(pids)

ret=requests.get(url)
print(ret)
print(ret.content)
'''


r'''
HACK:
ConfigParser, SafeConfigParser and RawConfigParser react with the no escaped "%" differently:
invalid interpolation syntax in '【北京市家电节能补贴 最高补贴13%！】' at position 17
Traceback (most recent call last):
ValueError: invalid interpolation syntax in '【北京市家电节能补贴 最高补贴13%！】' at position 17

'''