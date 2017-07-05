# -*- coding: utf-8 -*-

import itchat
from itchat.content import *
import sys
reload(sys)
sys.setdefaultencoding('utf-8')  #设置python的默认编码
import requests, time, re, HTMLParser, json, urllib,os,subprocess
import traceback
from sys import argv
from services.job import *
from util.callwin32api import *
from util.MysqlUtil import *
from util.RedisUtil import *
from services.weixincrawler import *
import datetime

html_parser = HTMLParser.HTMLParser()

@itchat.msg_register([TEXT, MAP, CARD, NOTE])
def text_reply(msg):

    msg_text = msg['Text']
    if len(msg_text) == 0:
        return
    
    pattern = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*,]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", re.IGNORECASE)
    match = pattern.match(msg_text)
    if match:
        urltopdf(match.group(),'')
    else:
        # print msg_text
        msg_arr = str.split(str(msg_text),' ')
        if len(msg_arr)>0:
            #判断是微信名称还是微信号
            r = re.compile(u'[\u4e00-\u9fa5]+',re.IGNORECASE)
            m = r.match(u''+msg_arr[0])
            if m:
                wxnum_arr = get_wxnum(msg_arr[0])
                itchat.send_msg(u'相关联的公众号:' + ','.join([''.join(x) for x in wxnum_arr]), msg['FromUserName'])
                return
            else:
                pass
        else:
            pass

        if len(msg_arr) == 3:
            wxnum = msg_arr[0]
            s_date = msg_arr[1]
            e_date = msg_arr[2]
        elif len(msg_arr) == 2:
            itchat.send_msg(u'两个参数可不行', msg['FromUserName'])
            return
        elif len(msg_arr) == 1:
            wxnum = msg_arr[0]
            s_date = str(datetime.date.today()-datetime.timedelta(days=1))
            e_date = None
        else:
            itchat.send_msg(u'要么一个要么三个', msg['FromUserName'])
            return

        pdf_files = begin_process(wxnum,s_date,e_date)
        for p_file in pdf_files:
            itchat.send_file(p_file, msg['FromUserName'])

pass


@itchat.msg_register([SHARING])
def sharingtopdf(msg):
    filename=u''+'"'+msg['Text']+'"'
    # urltopdf(msg['FromUserName'],msg['Url'],filename)
pass


def urltopdf(url , filename):

    
    #切换到phantomjs目录
    if str.find(os.getcwd(),'phantomjs') == -1:
        os.chdir(os.getcwd()+'\phantomjs')

    #文件名
    filename = filename.replace('|', '').replace('\\', '').replace(
        '/', '').replace(':', '').replace('*', '').replace('?', '').replace(
            '"', '').replace('<', '').replace('>', '').replace('&nbsp;', ' ')

    html_parser = HTMLParser.HTMLParser()
    article_url = html_parser.unescape(url)

    # print filename
    #执行
    cmd_method = "phantomjs url2pdf.js %s %s" % ('"' + url + '"', '"' +filename+ '"')

    # 原始方式
    # os.system(cmd_method.encode('gb2312'))

    # http://www.tuicool.com/articles/veaaYby
    p = subprocess.Popen(
        cmd_method.encode('gb2312'),
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)# .communicate()
    returncode = p.poll()
    while returncode is None:
        line = p.stdout.readline()
        returncode = p.poll()
        line = line.strip()
        if len(line) > 0:
            print line

    #发送
    all_file_path = os.getcwd()+"\\%s.pdf" % (filename)
    return all_file_path

pass


def get_wxnum(wxname):

    sql = "select wxnum from pb_wxnum where wxname='%s'" % (wxname)
    mysqlhelper = MysqlUtil()
    data = mysqlhelper.select(sql)
    if data[0] == 0:
        print u'数据库中没有找到微信号'
        return None
    else:
        return data[1]

pass


def begin_process(wxnum,s_date,e_date):

    wxnum = str(wxnum)
    sql = "select wxbiz from pb_wxnum where wxnum='%s'" % (wxnum)
    mysqlhelper = MysqlUtil()
    data = mysqlhelper.select(sql)
    if data[0] == 0:
        print u'数据库中没有找到biz,改为Sogou查找'
    else:
        print data[0]
        print data[1][0][0]

    wx_link = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s#wechat_redirect' % (data[1][0][0])
    job = Job((wxnum,wx_link))
    job.do_work()

    time.sleep(2)
    redis_client = RedisUtil()
    url = redis_client.get_out(wxnum)

    if url is None:
        print u'队列中没有此键值'
        raise Exception('队列中没有地址')

    # print url

    articles = crawler_wxnum_articles(url,s_date,e_date)
    # print articles[0][2][2]

    pdf_files =[]
    for target_list in articles:
        for target_sub in target_list:
            # print target_sub[2]
            # print html_parser.unescape(target_sub[3])
            pdf_files.append(urltopdf(target_sub[3],target_sub[2]))
        pass

    return pdf_files

pass


def main():

    try:

        wxnum = 'tianxiabj'
        s_date = '2017-07-01'
        e_date = None
        # begin_process(wxnum,s_date,e_date)
        # time.sleep(2)

        # url_par = url_params(url)

        # article_url = "%s&key=%s&ascene=%s&uin=%s&devicetype=%s&version=%s&pass_ticket=%s" % (
        #     html_parser.unescape(articles[0][0][3]),url_par[2], url_par[4],url_par[1],url_par[5],url_par[6],url_par[3]
        # )

        # detail_par = crawler_article_detail(article_url)

        # read_url = build_article_readcount_url(detail_par,articles[0][0][2],articles[0][0][4],url)

        # headers['Referer'] = article_url

        # data_post = {
        #     'is_only_read':'1',
        #     'req_id':detail_par[5],
        #     'pass_ticket':url_par[3],
        #     'is_temp_url':'0'
        # }

        # read_response = session.post(url=read_url, headers=headers,data=data_post, allow_redirects = True, verify=False)  # 最基本的GET请求
        # print read_response.text

        pass
    except Exception , e:

        msg = traceback.format_exc() # 方式1
        print e
        print msg
        pass

pass

if __name__ == '__main__':
    main()

# itchat.auto_login(enableCmdQR=True, hotReload=True)
itchat.auto_login(enableCmdQR=False, hotReload=True)
itchat.run()
