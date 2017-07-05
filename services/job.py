# -*- coding: utf-8 -*-

import win32ui,win32con,win32gui,win32api
import time
import clr
import sys
import redis

sys.path.append(r'D:\sourcecode\pythonsource\wxrobot\python4net')
clr.FindAssembly("FiddlerCore4")
clr.AddReference("FiddlerCore4")

from datetime import datetime
from Fiddler import *
from util.callwin32api import *
from util.MysqlUtil import * 
from helper.certificate import * 
from util.RedisUtil import * 

class Job(object):


    def __init__(self,task_info):
        
        '''
        初始化job


        params:taskinfo:(
            task_id,
            biz_url
        )

        '''


        if isinstance(task_info,tuple)==False:
            raise Exception('task_info must be a Tuple')

        pwin = is_wxlogin()

        set_foreground_window(pwin)

        self.redis_client = RedisUtil()
        self.rect = get_window_rect(pwin)
        self.task_id = task_info[0]
        self.biz_url = task_info[1]

    pass


     # will be invoked when it is called by delegate.
    def printLog(self,source,oLEA):
        print '\n** LogString: **\n'
        # print "\n** LogString: **\n" + oLEA.LogString
    pass


    def printSession(self,s):
        
        if s is None or s.oRequest is None or s.oRequest.headers is None:
            return
        if s.url.find('mp.weixin.qq.com/mp/getmasssendmsg?')==-1:
            return
        
        try:

            self.redis_client.set_in((str(self.task_id),'https://'+s.url))
            print self.task_id + u"链接获取成功"
            # print s.url
            FiddlerApplication.Shutdown()
            pass
        except Exception , e:

            msg = traceback.format_exc() # 方式1 
            print e
            print msg
            pass

    pass

    def onClose(sig):
        print 'closing'
        FiddlerApplication.Shutdown()
        print 'closed'
    pass

    def fiddler(self,flags):

        print 'init fiddler'
        FiddlerApplication.Log.OnLogString += self.printLog
        FiddlerApplication.AfterSessionComplete += self.printSession
        FiddlerApplication.SetAppDisplayName('httpwatch')
        CONFIG.IgnoreServerCertErrors = False
        FiddlerApplication.Startup(8877, flags)

    pass


    def get_point(self):

        """
        通过微信窗口坐标获取一系列操作坐标

        return:(
            窗体宽度,
            窗体高度,
            发送按钮X轴坐标,
            发送按钮Y轴坐标,
            消息输入框X轴坐标,
            消息输入框Y轴坐标,
            发送后消息X轴坐标,
            发送后消息Y轴坐标,
            左坐标,
            上坐标,
            右坐标,
            下坐标
        )

        exception:
        
        """

        if len(self.rect) != 4:
            raise Exception('坐标取值失败')
            pass

        x = self.rect[0]
        y = self.rect[1]
        right = self.rect[2]
        bottom = self.rect[3]

        return (
            right-x,
            bottom-y,
            right-71,
            bottom-25,
            right-71-183,
            bottom-25-59,
            right-71-183-19,
            bottom-25-59-100,
            self.rect[0],
            self.rect[1],
            self.rect[2],
            self.rect[3],
        )
    pass

   
    def do_work(self):

        """
        返回可以抓取文章的链接

        biz_url:需要点击的url

        return:

        """

        if isinstance(self.task_id,int):
            self.task_id = str(self.task_id)

        if len(self.task_id) == 0:
            raise Exception('请传入任务id')

        if len(self.biz_url) == 0:
            raise Exception('请传入biz地址')

        #设置各个点坐标
        point = self.get_point()
        print self.task_id + u"获取坐标成功"

        intPtr = is_wxlogin()

        #设置微信主窗体显示为当前窗体
        set_foreground_window(intPtr)

        #1.复制要发送消息到发送框中
        left_mouse_click(point[4],point[5])

        set_text(self.biz_url)
        time.sleep(2)
        get_text()
        time.sleep(2)

        #粘贴
        win32api.keybd_event(17,0,0,0)  #ctrl的键位码是17  
        win32api.keybd_event(86,0,0,0)  #v的键位码是86 
        win32api.keybd_event(86,0,win32con.KEYEVENTF_KEYUP,0) #释放按键  
        win32api.keybd_event(17,0,win32con.KEYEVENTF_KEYUP,0)  
        time.sleep(2)
        
        #2.(1)使用快捷键发送消息给好友
        set_foreground_window(intPtr)
        win32api.keybd_event(13,0,0,0)#Enter的键位码是13  
        win32api.keybd_event(13,0,win32con.KEYEVENTF_KEYUP,0) 

        print self.task_id + u"发送消息成功"

        #改变微信浏览器窗体大小
        change_wechat_window_size(point)
        time.sleep(2)

        # win32api.SetConsoleCtrlHandler(self.onClose, 1)
        import Fiddler as FC 
        prepareCert(FC)
        self.fiddler(1+512+32+2)

        #3.点击发送的消息获取地址
        left_mouse_click(point[6],point[7])
        
        print self.task_id + u"点击消息链接"

        # try:
        #     # keep console window be open        
        #     raw_input()
        # except:
        #     pass

    pass

