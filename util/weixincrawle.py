# -*- coding: utf-8 -*-

import HTMLParser


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