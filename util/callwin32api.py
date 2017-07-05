# -*- coding: utf-8 -*-

from win32api import GetSystemMetrics

import win32ui,win32con,win32gui,win32api
import win32clipboard as w

#,pyHook,pythoncom,win32gui ,wx


def is_wxlogin():

    """
    查找微信PC窗体

    return:微信窗体句柄

    exception：没有找到微信窗体
    """

    plogin = win32gui.FindWindow('WeChatLoginWndForPC', None)
    if plogin > 0 :
        raise Exception(u'微信没有登录')
        pass

    ploginout = win32gui.FindWindow('AlertDialog', None)
    if ploginout > 0 :
        raise Exception(u'微信没有登录')
        pass

    pwin = win32gui.FindWindow('WeChatMainWndForPC', None)
    if pwin == 0 :
        raise Exception(u'微信没有登录')
        pass
    else:
        return pwin


def set_foreground_window(intPtr):
    
    """
    通过窗体句柄将窗体设置为当前窗口

    intPtr:句柄

    exception:句柄无效

    """

    if intPtr <= 0:
        raise Exception('请传入有效的句柄')
        pass

    try:

        win32gui.SetForegroundWindow(intPtr)
        win32gui.ShowWindow(intPtr,4)
        pass
    except Exception as e:
        raise e
        pass

    pass


def get_window_rect(intPtr):

    """
    通过窗体句柄获取窗体坐标

    intPtr:句柄

    return:(
        左坐标,
        上坐标,
        右坐标,
        下坐标
    )

    exception:句柄无效

    """

    if intPtr <= 0:
        raise Exception('请传入有效的句柄')
        pass

    return win32gui.GetWindowRect(intPtr)
    pass


def change_wechat_window_size(rect):

    int_ptr = win32gui.FindWindow("CefWebViewWnd", None)
    if int_ptr == 0:
        print 'not found browser window'
        # raise Exception(u'没有找到发送消息窗体')
        pass
    else:
        win32gui.MoveWindow(int_ptr,rect[8],rect[9],rect[0]/2,rect[1]/2,False)
        pass
    pass


def left_mouse_click(link_x,link_y):

        """
        模拟鼠标左键单击

        link_x:要点击的消息X轴坐标

        link_y:要点击的消息Y轴坐标
                

        """

        #先移动鼠标到指定位置
        win32api.SetCursorPos((link_x,link_y))
        #按下鼠标左键
        win32api.mouse_event(
            win32con.MOUSEEVENTF_LEFTDOWN,
            link_x * 65536 / GetSystemMetrics(0), 
            link_y * 65536 / GetSystemMetrics(1), 
            0,0
        )
        #松开鼠标左键
        win32api.mouse_event(
            win32con.MOUSEEVENTF_LEFTUP,
            link_x * 65536 / GetSystemMetrics(0), 
            link_y * 65536 / GetSystemMetrics(1), 
            0,0
        )
        
        pass


def get_text():

    """
    读取剪切板 

    """

    w.OpenClipboard()  
    d = w.GetClipboardData(win32con.CF_TEXT)  
    w.CloseClipboard()  
    return d  


def set_text(content):
    """
    写入剪切板

    """

    w.OpenClipboard()  
    w.EmptyClipboard()  
    w.SetClipboardData(win32con.CF_TEXT, content)  
    w.CloseClipboard()  