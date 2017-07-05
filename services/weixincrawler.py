# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  #设置python的默认编码
from sys import argv
import requests
import traceback  
import HTMLParser
import cgi
import re
import json
import time
import random
import urllib
from util.MysqlUtil import *
from util.RedisUtil import *
from services.job import *

from fake_useragent import UserAgent
ua = UserAgent()


try:
    import cookielib
except:
    import http.cookiejar as cookielib

session = requests.session()
session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
html_parser = HTMLParser.HTMLParser()

headers = {
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 MicroMessenger/6.5.2.501 NetType/WIFI WindowsWechat',
    'Accept-Language':
    'zh-CN,zh;q=0.8,en-us;q=0.6,en;q=0.5;q=0.4'
}

def log(str):


    with open('/test.txt', 'w') as f:
        f.write(str)

pass


def is_need_to_add(s_date_timespan,e_date_timespan,publish_date):

    """
    文章是否需要添加到数组中

    param:s_date_timespan 开始时间戳
    param:e_date_timespan 结束时间戳
    param:publish_date    文章发布时间戳
    
    return:true or false

    """

    if (s_date_timespan <>0 and s_date_timespan - int(publish_date) > 0):
        return False
    
    if (e_date_timespan <> 0 and e_date_timespan - int(publish_date) < 0):
        return False

    return True

pass


def build_article(content,s_date_timespan,e_date_timespan):
    
    """
    创建微信文章实体
    
    params:content json内容
    
    params:article_extend_info(
        article_comment_id,
        article_ct,
        wxtoken
    ) 文章扩展内容

    return:[(
        id,#文章id
        datetime,#发布时间时间戳
        title,#标题
        content_url,#文章地址
        article_comment_id,
        article_ct,
        wxtoken
    )]

    """

    if len(content) == 0:
        return None

    articles = []

    # print '=================='
    jsonobj = json.loads(content)
    for item in jsonobj['list']:
         
        comm_msg_info = item['comm_msg_info']
        app_msg_ext_info = item['app_msg_ext_info']

        if not is_need_to_add(s_date_timespan,e_date_timespan,comm_msg_info['datetime']):
            continue

        if len(app_msg_ext_info['title']) > 0:
            
            articles.append([
                comm_msg_info['id'],
                comm_msg_info['datetime'],
                app_msg_ext_info['title'], 
                html_parser.unescape(app_msg_ext_info['content_url'].replace("#wechat_redirect",'')),
                '1'
            ])
        pass

        
        multi_app_msg_item_list = app_msg_ext_info['multi_app_msg_item_list']

        for index,target_list in enumerate(multi_app_msg_item_list):

            if len(target_list['title']) == 0:
                continue

            articles.append([
                comm_msg_info['id'],
                comm_msg_info['datetime'],
                target_list['title'], 
                html_parser.unescape(target_list['content_url'].replace("#wechat_redirect",'')),
                str(index+1)
            ])

        pass
    
    return articles
pass


def is_can_continue(content,s_date_timespan,min_pb_time,is_first_page = False):

    """
    文章是否可以继续抓取

    params:is_first_page 是否第一次请求

    return:true or false

    """

    is_date_end =True if (s_date_timespan-int(min_pb_time))<0 else False

    if is_first_page:
        match_is_can = re.match(r".*can_msg_continue = '(.+?)'.*?;", content , re.DOTALL)
        if match_is_can:
            return True if (int(match_is_can.group(1)) == 1 and is_date_end) else False
        else:
            return False
    else:
        jsonobj = json.loads(content)
        return True if (int(jsonobj['can_msg_continue']) == 1 and is_date_end) else False
pass


def get_next_pageurl(biz,frommsgid,count,uin,key,pass_ticket):

    """
    得到翻页文章链接
    """

    str_format = "https://mp.weixin.qq.com/mp/profile_ext?action=getmsg&__biz=%s&f=json&frommsgid=%s&count=%s&scene=124&is_ok=1&uin=%s&key=%s&pass_ticket=%s&wxtoken=&x5=0&f=json"
    return str_format % (biz,frommsgid,count,uin,key,pass_ticket)
pass


def url_params(url):

    """
    解析url中的参数


    params:url 请求地址

    return:(
        biz,
        uin,
        key,
        pass_ticket,
        ascene,
        devicetype,
        version
    )
    """

    biz_match = re.match(r'.*biz=(.*?)&', url , re.DOTALL)
    biz = biz_match.group(1)
    uin_match = re.search(r'.*uin=(.*?)&', url , re.DOTALL)
    uin = uin_match.group(1)
    key_match = re.match(r'.*key=(.*?)&', url , re.DOTALL)
    key = key_match.group(1)
    pass_ticket_match = re.match(r'.*pass_ticket=(.*?)&', url+'&' , re.DOTALL)
    pass_ticket = pass_ticket_match.group(1)
    ascene_match = re.match(r'.*ascene=(.*?)&', url , re.DOTALL)
    ascene = ascene_match.group(1) if ascene_match else ''
    devicetype_match = re.match(r'.*devicetype=(.*?)&', url , re.DOTALL)
    devicetype = devicetype_match.group(1)
    version_match = re.match(r'.*version=(.*?)&', url , re.DOTALL)
    version = version_match.group(1)

    
    return (
        biz,
        uin,
        key,
        pass_ticket,
        ascene,
        devicetype,
        version
    )

pass


def build_article_readcount_url(detail_params,article_title,idx,url):

    """
    构造阅读数地址


    """

    url_par = url_params(url)
    r = random.random()

    str_format = (
        "https://mp.weixin.qq.com/mp/getappmsgext?"
        "__biz=%s&appmsg_type=9&mid=%s&sn=%s&idx=%s&scene=%s&%s&ct=%s&abtest_cookie=&devicetype=%s&version=&f=json"
        "&r=%s&is_need_ad=0&comment_id=%s&is_need_reward=0&both_ad=1&reward_uin_count=0&msg_daily_idx=%s&%s&key=%s"
        "&pass_ticket=%s&wxtoken=%s&%s&clientversion=%s&x5=0&f=json"
    )
    
    # print detail_params[9]
    title_par = {'title':article_title}
    uin_pa = {'uin':url_par[1]}
    dd = {'devicetype':detail_params[9]}
    print urllib.urlencode(dd)
    return str_format % (url_par[0],str(detail_params[3]),str(detail_params[4]),str(idx),detail_params[6],urllib.urlencode(title_par),
        str(detail_params[1]),detail_params[9].replace("&nbsp;", " "),str(r),str(detail_params[0]),detail_params[8],
        urllib.urlencode(uin_pa),url_par[2],url_par[3],str(detail_params[2]),urllib.urlencode(dd),detail_params[7]
    )

pass


def crawler_article_detail(article_url):

    """
    抓取文章详情、阅读数、点赞数、评论


    return:(
        article_comment_id,
        article_ct,
        wxtoken,
        mid,
        sn,
        req_id,
        scene,
        clientversion,
        msg_daily_idx,
        devicetype
    )

    """

    article_url = html_parser.unescape(article_url)

    article_response = session.get(url=article_url, headers=headers, allow_redirects = True, verify=False)  # 最基本的GET请求
    if article_response.status_code != 200:
        raise Exception('request article content fail')
        pass

    scene_match = re.match(r'.*scene=(.*?)&', article_url+'&' , re.DOTALL)
    scene = scene_match.group(1)

    article_comment_id_match = re.match(r'.*var comment_id = "(.*?)" *', article_response.text , re.DOTALL)
    article_comment_id = article_comment_id_match.group(1)

    article_ct_match = re.match(r'.*var ct = "(.*?)";', article_response.text , re.DOTALL)
    article_ct = article_ct_match.group(1)

    mid_match = re.match(r'.*var mid = "(.*?)"', article_response.text , re.DOTALL)
    mid = mid_match.group(1)

    sn_match = re.match(r'.*var sn = "(.*?)"', article_response.text , re.DOTALL)
    sn = sn_match.group(1)

    req_id_match = re.match(r".*var req_id = '(.*?)';", article_response.text , re.DOTALL)
    req_id = req_id_match.group(1)

    clientversion_match = re.match(r'.*var clientversion = "(.*?)";', article_response.text , re.DOTALL)
    clientversion = clientversion_match.group(1)

    wxtoken_match = re.match(r'.*window.wxtoken = "(.*?)";', article_response.text , re.DOTALL)
    wxtoken = wxtoken_match.group(1)

    msg_daily_idx_match = re.match(r'.*var msg_daily_idx = "(.*?)"', article_response.text , re.DOTALL)
    msg_daily_idx = msg_daily_idx_match.group(1)

    devicetype_match = re.match(r'.*var devicetype = "(.*?)";', article_response.text , re.DOTALL)
    devicetype = devicetype_match.group(1)
    devicetype = devicetype.replace("\\x26", "&")

    # print article_comment_id
    # print article_ct
    # print wxtoken
    # print mid
    return (
        article_comment_id,
        article_ct,
        wxtoken,
        mid,
        sn,
        req_id,
        scene,
        clientversion,
        msg_daily_idx,
        devicetype
    )
    
    
pass


def crawler_wxnum_articles(url,s_date,e_date,count = 10):

    """
    抓取文章
    """

    s_date_timespan = 0 if s_date is None else int(time.mktime(time.strptime(s_date,'%Y-%m-%d')))
    e_date_timespan = 0 if e_date is None else int(time.mktime(time.strptime(e_date,'%Y-%m-%d')))

    r = session.get(url=url, headers=headers, allow_redirects = True, verify=False)  # 最基本的GET请求

    if r.text.find(u'请在微信客户端打开链接')>-1:
        raise Exception('link url time out')

    # print r.cookies
    # print session.cookies
    # localtion_url = r.headers['Location']

    pattern = re.compile(r"var msgList = (.*);", re.IGNORECASE)
    match = pattern.search(r.text)
    str = match.group(1).replace("\\","").replace("&quot;","\"").strip("'")

    articles = []
    new_article = build_article(str,s_date_timespan,e_date_timespan)
    
    if new_article is None:
        raise Exception('没有采集到文章')

    frommsgid = new_article[int(len(new_article)-1)][0]
    min_pb_time = new_article[int(len(new_article)-1)][1]
    can_continue = is_can_continue(r.text,s_date_timespan,min_pb_time,True)

    if e_date is None or (e_date_timespan - int(new_article[0][1]) >0):
        articles.append(new_article)

    url_par = url_params(url)

    # while can_continue:
        
    #     time.sleep(2)
    #     next_url = get_next_pageurl(url_par[0],frommsgid,count,url_par[1],url_par[2],url_par[3])
    #     next_response = session.get(url=next_url,headers=headers,verify=False)

    #     if next_response.status_code == 200:
    #         jsonobj = json.loads(next_response.text)
    #         nn_article = build_article(jsonobj['general_msg_list'],s_date_timespan,e_date_timespan)
    #         frommsgid = nn_article[int(len(nn_article)-1)][0]
    #         min_pb_time = nn_article[int(len(nn_article)-1)][1]
    #         can_continue = is_can_continue(next_response.text,e_date_timespan,min_pb_time)

    #         if s_date is None or (s_date_timespan - int(nn_article[0][1]) > 0):
    #            articles.append(nn_article)

    #         articles.append(nn_article)

    return articles


pass


def find_wxbiz(wxname,wxnum):

    '''
    通过微信名字或者微信号找到微信的biz
    '''

    if len(wxname)+len(wxnum)==0:
        raise Exception('args not null')

    # html_parser = HTMLParser.HTMLParser()

    #命令行传参需要对参数进行编码
    # url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_=" % (
    #     urllib.quote(wxname.decode(sys.stdin.encoding).encode('utf8')))

    search_key = wxnum if len(wxnum)>0 else wxname
    url = "http://weixin.sogou.com/weixin?type=1&s_from=input&query=%s&ie=utf8&_sug_=n&_sug_type_=" % (
        search_key)
    
    headers['User-Agent'] = ua.random
    # requests.meta['proxy'] = 
    r = requests.get(url=url, headers=headers, verify=False)  # 最基本的GET请求

    content = r.content.decode("utf8", "ignore").encode("gbk", "ignore")
    #print content

    pattern = re.compile(
        r"<a target=[\S]+? uigs=[\S]account_name_0[\S] href=[\S]([\w\W]+?)[\S]>([\w\W]+?)</a>",
        re.DOTALL)
    print content
    match = pattern.match(content)

    if match:

        print u'抓取到公众号列表链接'
        listurl = html_parser.unescape(match[0][0])

        wxnuminfo_response = requests.get(url=listurl, headers=headers, verify=False)  # 最基本的GET请求
        wxbiz_pattern = re.compile(r'var[\S]biz[\S]=[\S]"([\w\W]+?)"[\S]||[\S]"";',re.DOTALL)
        wxbiz_match = wxbiz_pattern.match(wxnuminfo_response.content)
        if wxbiz_match:
            print wxbiz_match.group()
            return wxbiz_match.group()
        else:
            return None

    else:
        print u'没有找到公众号biz'
        return None

pass


# try:

    # url = 'https://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzA5NTIwNjc5MQ==&uin=MTA5MTMxMDAyMQ%3D%3D&key=c5a673ba6130fcd938543bc6ea1c7afcc349c67381f9f0970e6757c204d9a99593235471fadbcd0461fe5e749a37e48a40c0f511d7c36dc87a8231f0e0fb7aeaad56c3d26f67124e49cd9ad761d09d00&devicetype=Windows+UnKnow&version=62040525&lang=zh_CN&ascene=7&pass_ticket=%2BP3NNAv4KccdSzL3PiSVXLZdkP5JIAU7BALv%2FKIHvezSGrFwtJ3F7Dn6a6tv%2Brif'
    # url = 'https://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzA5NTIwNjc5MQ==&uin=MTA5MTMxMDAyMQ%3D%3D&key=c5a673ba6130fcd938543bc6ea1c7afcc349c67381f9f0970e6757c204d9a99593235471fadbcd0461fe5e749a37e48a40c0f511d7c36dc87a8231f0e0fb7aeaad56c3d26f67124e49cd9ad761d09d00&devicetype=Windows+UnKnow&version=62040525&lang=zh_CN&pass_ticket=%2BP3NNAv4KccdSzL3PiSVXLZdkP5JIAU7BALv%2FKIHvezSGrFwtJ3F7Dn6a6tv%2Brif'
    # ascene_match = re.match(r".*ascene=(.*?)&", url , re.DOTALL)
    # print ascene_match.group(1) if ascene_match else 'none'

    # argv[1]
    # sql = "select wxbiz from pb_wxnum where wxnum='%s'" % ('tianxiabj')
    # mysqlhelper = MysqlUtil()
    # data = mysqlhelper.select(sql)
    # if data[0] == 0:
    #     print u'数据库中没有找到'
    # else:
    #     print data[0]
    #     print data[1][0][0]

    # wx_link = 'http://mp.weixin.qq.com/mp/getmasssendmsg?__biz=%s#wechat_redirect' % (data[1][0][0])
    # job = Job(('tianxiabj',wx_link))
    # job.do_work()

    # redis_client = RedisUtil()
    # while True:
    #     if redis_client.r.exists('tianxiabj'):
    #         url = redis_client.r.get('tianxiabj')
    #         break
    #     else:
    #         print '没有找到'
    #         time.sleep(2)

    # find_wxbiz('','tianxiabj')
    # str = "请在微信中打开此链接"
    # print str.find('请在微信客户端打开链接')

    # a = "2013-10-10 23:40:00"
    # print time.strptime(a, "%Y-%m-%d %H:%M:%S")
    # print int(time.mktime(time.strptime(a,'%Y-%m-%d %H:%M:%S')))
    # print time.time()
    # print time.strftime('%Y-%m-%d',time.localtime(time.time()))
    
    # s_date = None
    # e_date = '2017-06-28'
    # url = 'https://mp.weixin.qq.com/mp/getmasssendmsg?__biz=MzA5NTIwNjc5MQ==&uin=MTA5MTMxMDAyMQ%3D%3D&key=c5a673ba6130fcd938543bc6ea1c7afcc349c67381f9f0970e6757c204d9a99593235471fadbcd0461fe5e749a37e48a40c0f511d7c36dc87a8231f0e0fb7aeaad56c3d26f67124e49cd9ad761d09d00&devicetype=Windows+UnKnow&version=62040525&lang=zh_CN&ascene=7&pass_ticket=%2BP3NNAv4KccdSzL3PiSVXLZdkP5JIAU7BALv%2FKIHvezSGrFwtJ3F7Dn6a6tv%2Brif'
    # articles = crawler_wxnum_articles(url,s_date,e_date)
    # print len(articles)
    # print articles
    # print articles[0][2][2]
    # for target_list in articles:
    #     target_list
    #     pass
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

#     pass
# except Exception , e:

#     msg = traceback.format_exc() # 方式1 
#     print e
#     print msg
#     pass
