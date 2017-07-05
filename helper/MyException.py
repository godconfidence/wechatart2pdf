from __future__ import division
import traceback

class MyException(Exception):
    # def __init__(self,x,y):
    #     Exception.__init__(self,x,y)
    #     self.x = x
    #     self.y = y
    def __init__(self,value):
        self.value=value
    def __str__(self):
        return repr(self.value)

if __name__ == '__main__' :

    try:

        x = 2
        y = 3

        if x % y > 0 :
            print x/y
            raise MyException('22')
        pass
    except MyException as mye:
        print mye
     