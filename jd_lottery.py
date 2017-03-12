#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

import re
import time,datetime
import httplib2,urllib.request,http.cookiejar
from multiprocessing.dummy import Pool as ThreadPool

import random

import smtplib
from email.mime.text import MIMEText

import configparser#read and save configuration.
import ast
import json

import sys,os
import webbrowser
import codecs

class TimeoutExpired(Exception):
    pass

try:
    import msvcrt
    
    def readInput(caption, default, timeout=10):
        start_time = time.time()
        sys.stdout.write('%s(%d秒自动跳过):' % (caption,timeout))
        sys.stdout.flush()
        input = ''
        while True:
            ini=msvcrt.kbhit()
            try:
                if ini:
                    chr = msvcrt.getche()
                    if ord(chr) == 13:  # enter_key
                        break
                    elif ord(chr) >= 32:
                        input += chr.decode()
            except Exception as e:
                pass
            if len(input) == 0 and time.time() - start_time > timeout:
                break
        print ('')  # needed to move to next line
        if len(input) > 0:
            return input+''
        else:
            return default
except:
    import signal
    def alarm_handler(signum, frame):
        raise TimeoutExpired

    def readInput(caption, default, timeout=10):
        # set signal handler
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout) # produce SIGALRM in `timeout` seconds

        try:
            return input('%s(%d秒自动跳过):' % (caption,timeout))
        except:
            print(default)
            return default
        finally:
            signal.alarm(0) # cancel alarm

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
    Read settings from config.ini .
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config=configparser.ConfigParser(delimiters=('='), allow_no_value=True)
        with codecs.open('config.ini', "r", "utf-8") as f:
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

    def get_valid_time(self):
        try:
            time_str=self.config.get("通用设置", "放水间隔")
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

    def get_draw_time(self):
        try:
            time_str=self.config.get("通用设置", "抽奖间隔")
            seconds=1
            seconds=seconds*int(time_str)
            if seconds>0:
                return seconds
            else:
                return 10
        except Exception as e:
            print(str(e))
            return 10
            
            
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

    def GetFileList(self, dir, fileList):
        newDir = dir
        if os.path.isfile(dir):
            fileList.append(dir)
        elif os.path.isdir(dir):  
            for s in os.listdir(dir):
                if s.endswith('.txt'):
                    newDir=os.path.join(dir,s)
                    self.GetFileList(newDir, fileList)  
        return fileList

    def get_users(self):
        users = {}
        uid = 0
        for e in COOKIES:
            uid += 1
            users[uid] = e
        return users

    def get_user(self):
        print('')
        uid = 0
        for k in users:
            uid += 1
            print(str(k)+') '+users[k])
        u=int(input('\n请选择用户：'))
        if u in users.keys():
            user = users[u].replace('\\','/').split('/')
            user = user[1].split('.')
            user = user[0]
            print('\n你选择了: '+user+'')
            return u
        else:
            print('\n用户不存在，请重输！')
            self.get_user()
            
settings = Settings()
s=requests.session()

MAX_PRICE=10000000
#SLEEP_INTERVAL seconds.
SLEEP_INTERVAL=settings.get_sleep_interval()
MONITORING_CODE=settings.get_MONITORING_CODE()
VALID_TIME=settings.get_valid_time()
DRAW_TIME=settings.get_draw_time()
DEBUG=settings.is_debug()

PLAY_MUSIC=settings.is_play_music()
MUSIC_PATH=settings.get_music_path()
SEND_EMAIL=settings.is_send_email()
SENDER_MAIL_SERVER=settings.get_sender_email_server()
SENDER_EMAIL_ACCOUNT=settings.get_sender_email_account()
SENDER_EMAIL_PASSWD=settings.get_sender_email_passwd()
RECEIVER_EMAIL_ACCOUNTS=settings.get_receiver_email_account()

COOKIES = settings.GetFileList('cookies', [])
USERS = settings.get_users()

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
            'User-Agent':'Mozilla/5.0(WindowsNT6.3;WOW64;rv:47.0)Gecko/20100101Firefox/47.0',
            'Accept':'*/*',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
            'Referer':'http://www.jd.com/',
            'Connection':'keep-alive'}
            req=s.get(self.url,headers=headers,timeout=10)
            if req.status_code != requests.codes.ok:
                raise Exception(req.status_code)
            self.page=req.text
        except Exception as e:
            print(str(e))
            beep()
            print(time.ctime())
            print("无法下载网页。1秒后重试...")
            time.sleep(1)
            self.__init__(self.code_i)
            self.load_html()
        self.html=self.page
        return self.html

class Result:
    """
    Read/save goods info from/to result.txt.
    """
    def __init__(self):
        self._read_ini()

    def _read_ini(self):
        self.config = configparser.RawConfigParser()
        self.config.read('result.txt')
        
    def get_url(self, code):
        try:
            return self.config.get(code, 'url')
        except Exception as e:
            print(str(e))
            return ''
            
    def set_url(self, code, _str):
        string = str(_str)
        with open('result.txt', 'w') as configfile:
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
        with open('result.txt', 'w') as configfile:
            if not self.config.has_section(code): self.config.add_section(code)
            self.config.set(code, 'res', string)
            self.config.write(configfile)
            
def internet_on():
    """Check if computer is online. Return type: boolean."""
    try:
        response=s.get("http://www.baidu.com",timeout=10)
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

def get_webservertime(wintime):
    while True:
        try:
            conn=httplib2.Http(timeout=10)
            resp, content=conn.request("http://ls-activity.jd.com", "GET")
            #r.getheaders() #获取所有的http头
            ts=resp['date'] #获取http头date部分
            #将GMT时间转换成北京时间
            ltime= time.strptime(ts[5:25], "%d %b %Y %H:%M:%S")
            nowtime=time.localtime(time.mktime(ltime)+8*60*60)
            date=str(nowtime[0])+'-'+str(nowtime[1])+'-'+str(nowtime[2])
            print('\n时间校对: '+str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+' / '+str(nowtime[0])+'-'+str(nowtime[1])+'-'+str(nowtime[2])+' '+str(nowtime[3])+':'+str(nowtime[4])+':'+str(nowtime[5]))
            print('上次放水时间：'+str(wintime))
            wintime=time.strptime(str(wintime),'%Y-%m-%d %H:%M:%S')
            wintime=datetime.datetime(wintime[0],wintime[1],wintime[2],wintime[3],wintime[4],wintime[5])
            nowtime=datetime.datetime(nowtime[0],nowtime[1],nowtime[2],nowtime[3],nowtime[4],nowtime[5])
            return {'date': date, 'delaytime': (nowtime-wintime).seconds}
        except Exception as e:
            print(str(e))
            beep()
            print(time.ctime())
            print("无法获取服务器时间。1秒后重试...")
            time.sleep(1)
        

def get_page(user):
    cj=http.cookiejar.MozillaCookieJar()
    cj.load(user,ignore_expires=True,ignore_discard=True)
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    urllib.request.install_opener(opener)
    headers={'Host':'l-activity.jd.com',
    'User-Agent':'Mozilla/5.0(WindowsNT6.3;WOW64;rv:47.0)Gecko/20100101Firefox/47.0',
    'Accept':'application/json,text/javascript,*/*;q=0.01',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'X-Requested-With':'XMLHttpRequest',
    'Referer':'http://www.jd.com',
    'Connection':'keep-alive'}
    #opener.addheaders = [('Host', 'l-activity.jd.com'), ('User-Agent', 'Mozilla/5.0(WindowsNT6.3;WOW64;rv:47.0)Gecko/20100101Firefox/47.0'), ('Accept', '*/*'), ('X-Requested-With', 'XMLHttpRequest'), ('Referer', 'http://www.jd.com'), ('Connection', 'keep-alive')]
    user = user.replace('\\','/').split('/')
    user = user[1].split('.')
    user = user[0]
    if CODE_PENDING in OUT.keys() and 'user' in OUT[CODE_PENDING].keys() and user == OUT[CODE_PENDING]['user'] and time.strptime(OUT[CODE_PENDING]['date'], "%Y-%m-%d")[2] == time.strptime(SERVERDATE, "%Y-%m-%d")[2]:
        print('当天抽奖次数已用完...\n')
        return False
    
    DRAW_URL="http://l-activity.jd.com/lottery/lottery_start.action?callback=&lotteryCode=%s&_=%d"%(CODE_PENDING, int(time.time()*1000))
    req=urllib.request.Request(DRAW_URL,headers=headers)

    for i in range(0,3,1):
        #response=urllib.request.urlopen(req,timeout=6)
        #response=urllib.request.urlopen(DRAW_URL, timeout=6)
        try:
            response=opener.open(req, timeout=6)
            page=response.read().decode('utf-8', 'ignore')
            print(datetime.datetime.now().strftime('%H:%M:%S')+' / '+user+': '+str(page))
            page=json.loads(page)
            if "data" in page.keys():
                page = page['data']
                if page['chances'] == 0:
                    OUT[CODE_PENDING] = {}
                    OUT[CODE_PENDING]['user'] = user
                    OUT[CODE_PENDING]['date'] = SERVERDATE
                DREW = True
            page['userPin'] = page['userPin'] if 'userPin' in page and page['userPin'] else user
            page['drawTime'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            page = json.dumps(page)
            with codecs.open('src/draw.js', 'a', 'utf-8') as draw:
                draw.write('draw["'+CODE_PENDING+'"].push('+page+');\n')
        except Exception as e:
            print(str(e))
        time.sleep(DRAW_TIME)

def Run():

    global OUT, DREW, DRAW_URL
    #dict 存储当天已用完抽奖次数的结果
    OUT = {}
    DREW = False
    #Counting querying times.
    count=0
    #JD goods id.
    CODE=re.findall(r"(\w{8}-\w{4}-\w{4}-\w{4}-\w{12})", MONITORING_CODE)
    CODE=list(set(CODE))
    while(True):
        clean=readInput('\n是否清理抽奖记录（Y/N）', 'N').upper()
        if clean in ['Y', 'N']:
            clean='w' if clean == 'Y' else 'a'
            break
        else:
            print('输入不正确！清理（Y）/保留（N）：')
            
    with codecs.open('src/draw.js', clean, 'utf-8') as draw:
        draw.write('var draw={};\n')
        for c in CODE:
            draw.write('draw["'+c+'"] = [];\n')
            
    while(True):
        #Format output
        #with codecs.open('output.html', 'w', 'utf-8') as html:
        #    html.write(u'<!DOCTYPE html>\n<html>\n    <head>\n        <meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0"/>\n        <meta name="format-detection" content="telephone=no" />\n        <meta http-equiv="refresh" content="10">\n        <title>京东抽奖测水</title>\n        <link href="src/bootstrap.min.css" rel="stylesheet" type="text/css" />\n        <script type="text/javascript" src="src/jquery-3.1.0.min.js"></script>\n        <script type="text/javascript" src="src/data.js"></script>\n        <script type="text/javascript" src="src/angular.min.js"></script>\n        <script type="text/javascript" src="src/init.js"></script>\n    </head>\n    <body>\n        <div ng-app="data" class="container">\n            <div ng-controller="list" class="table-responsive">\n                <div ng-repeat="(code, res) in result">\n                <table class="table table-striped">\n                    <caption>用户列表:  {{code}}</caption>\n                    <tr>\n                        <th>优惠券名称</th>\n                        <th>用户</th>\n                        <th>时间</th>\n                    </tr>\n                    <tr ng-repeat="item in res track by $index">\n                        <td>{{item.prizeName}}</td>\n                        <td>{{item.userPin}}</td>\n                        <td>{{item.winDate}}</td>\n                     </tr>\n                </table>\n                </div>\n            </div>\n        </div>')
        with codecs.open('src/data.js', 'w', 'utf-8') as data:
            data.write('var data = {};')
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
            DRAW_URL="http://l-activity.jd.com/lottery/lottery_start.action?callback=&lotteryCode=%s&_=%d"%(code_i, int(time.time()*1000))
    
            print("++++++++++++++++++++++++++++++++++++++++++++++++++++")

            product=Product(code_i)

            result=Result()
            prev_url=result.get_url(code_i)
            prev_data=result.get_data(code_i)
            news=False
            match=None

            curr_data=product.load_html()

            #save url to file if url not saved:
            if prev_url!=url_i:
                result.set_url(code_i, url_i)

            ########################################################
            #data changed：
            if curr_data!=prev_data:
                news=True
                result.set_data(code_i, curr_data)
                keyword=re.search(code_i+"\|"+".*", MONITORING_CODE)
                if keyword:
                    keyword=keyword.group(0).split("|")[1]
                    match=re.search("{\"prizeName\"\s*:\s*\"[^\"]*"+keyword+"[^\"]*\"[^}]*}", curr_data)
                    if match:
                        match=json.loads(match.group())
                        delaytime=get_webservertime(match['winDate'])
                        global SERVERDATE
                        SERVERDATE = delaytime['date']
                        delaytime = delaytime['delaytime']
                        if delaytime <= int(VALID_TIME):
                            global CODE_PENDING
                            CODE_PENDING = code_i
                            pool = ThreadPool(len(USERS))
                            results = pool.map(get_page, COOKIES)
                            pool.close()
                            pool.join()
                        

            #detection finished.
            ########################################################

            message = u"数据      ："+curr_data+"\n"+          \
                      u"网址      ："+url_i+"\n"+              \
                      u"抽奖      ："+DRAW_URL+"\n"

            if DREW:
                print("\n检测到变更！！！")
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
                print("无变更。\n")
                
            with codecs.open('src/data.js', 'a', 'utf-8') as data:
                data.write('\ndata["' + code_i + '"] = ' + curr_data + ';')
                
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
        #with codecs.open('output.html', 'a', 'utf-8') as html:
        #    html.write(u'\n    </body>\n</html>')
            
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
            print(str(e))
            beep()
            time.sleep(5)
