# -*- coding: utf-8 -*-

import itchat, time
from itchat.content import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  #设置python的默认编码
import requests, time, re, HTMLParser, json, urllib,os,subprocess
from sys import argv
from util.callwin32api import *
from util.MysqlUtil import * 
from services.job import * 
from ctypes import *

@itchat.msg_register([TEXT, MAP, CARD, NOTE])
def text_reply(msg):

    # itchat.send(msg['Text'], msg['FromUserName'])

    headers = {
        'Accept':
        'text/html, application/xhtml+xml, image/jxr, */*',
        'user-agent':
        'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
        'Accept-Language':
        'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'
    }

    pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE)
    match = pattern.match(msg['Text'])
    if match:
        urltopdf(match.group(),'')
    else:
        articles = find_wx(msg['Text'], headers)
        itchat.send(str(len(articles))+u'篇文章', msg['FromUserName'])

        # for target_list in articles:
        #     all_file_path = urltopdf(target_list[1], target_list[0])
        #     time.sleep(2)
        #     #发送文件
        #     itchat.send_file(all_file_path, msg['FromUserName'])
        # pass
    pass

pass


@itchat.msg_register([SHARING])
def sharingtopdf(msg):
    filename=u''+'"'+msg['Text']+'"'
    # urltopdf(msg['FromUserName'],msg['Url'],filename)
pass


# 解析公众号
def find_wx(wxname, headers):

    html_parser = HTMLParser.HTMLParser()

    #命令行传参需要对参数进行编码
    # url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_=" % (
    #     urllib.quote(wxname.decode(sys.stdin.encoding).encode('utf8')))

    url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_=" % (
        wxname)

    r = requests.get(url=url, headers=headers, verify=False)  # 最基本的GET请求

    content = r.content.decode("utf8", "ignore").encode("gbk", "ignore")
    #print content

    pattern = re.compile(
        r"<a target=[\S]+? uigs=[\S]account_name_0[\S] href=[\S]([\w\W]+?)[\S]>([\w\W]+?)</a>",
        re.IGNORECASE)

    match = pattern.findall(content)

    if match:
        print u'抓取到公众号列表链接'
        listurl = html_parser.unescape(match[0][0])
        return find_wx_articles(listurl, headers)
    else:
        print u'没有找到公众号'
        return null


pass


def find_wx_articles(url, headers):

    html_parser = HTMLParser.HTMLParser()

    r = requests.get(url=url, headers=headers, verify=False)  # 最基本的GET请求

    pattern = re.compile(r"var msgList = (.*);", re.IGNORECASE)

    match = pattern.search(r.content)
    jsonobj = json.loads(match.group(1))
    articles = []

    for item in jsonobj['list']:

        app_msg_ext_info = item['app_msg_ext_info']
        articles.append([
            app_msg_ext_info['title'], 'http://mp.weixin.qq.com' +
            html_parser.unescape(app_msg_ext_info['content_url'])
        ])

        # multi_app_msg_item_list = app_msg_ext_info['multi_app_msg_item_list']
        # for target_list in multi_app_msg_item_list:
        #     articles.append([
        #         target_list['title'], 'http://mp.weixin.qq.com' +
        #         html_parser.unescape(target_list['content_url'])
        #     ])

        # pass

    pass
    print len(articles)
    return articles


pass


def urltopdf(url, filename):

    #切换到phantomjs目录
    os.chdir('D:\sourcecode\htmlsource\phantomjs')

    #文件名
    filename = filename.replace('|', '').replace('\\', '').replace(
        '/', '').replace(':', '').replace('*', '').replace('?', '').replace(
            '"', '').replace('<', '').replace('>', '')

    html_parser = HTMLParser.HTMLParser()
    article_url = html_parser.unescape(url)

    #执行
    cmd_method = "phantomjs loadpage.js %s %s" % ('"' + url + '"', filename)
    subprocess.Popen(
        cmd_method.encode('gb2312'),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).communicate()

    #发送
    all_file_path = "D:\\sourcecode\\htmlsource\\phantomjs\\%s.pdf" % (filename)
    return all_file_path

pass


# headers = {
#         'Accept':
#         'text/html, application/xhtml+xml, image/jxr, */*',
#         'user-agent':
#         'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
#         'Accept-Language':
#         'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'
# }

# pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE)
# match = pattern.match(argv[1])
# if match:
#     urltopdf(match.group(),'')
# find_wx(argv[1],headers)
# itchat.auto_login(enableCmdQR=True, hotReload=True)
# itchat.run()

# print argv[1]

job = Job()
job.do_work(1,'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzA3NTk0NTEwOA==#wechat_redirect')
