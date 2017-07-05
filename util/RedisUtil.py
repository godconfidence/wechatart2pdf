# -*- coding: utf-8 -*-

import redis


class RedisUtil(object):


    def __init__(self):

        pool = redis.ConnectionPool(host='127.0.0.1', port=6379,db=0)  
        self.r = redis.Redis(connection_pool=pool) 
        # self.r = redis.Redis(host='127.0.0.1', port=6379,db=0)

    pass

    
    def set_in(self,args):
       
        """
        string类型键值添加

        param:args(
            key,
            value
        )

        exception
        """

        if self.r is None:
            raise Exception('redis is not connection')

        if isinstance(args,tuple)==False:
            raise Exception('args must be a Tuple')
        
        try:
            self.r.set(args[0],args[1])
            self.r.expire(args[0],3600)
            print 'set in redis success'
        except Exception as identifier:
            raise identifier

    pass

    def get_out(self,key):

        """
        获取string类型数据
        """

        if self.r is None:
            raise Exception('redis is not connection')
        
        if len(key) == 0:
            raise Exception("ken can't be empty")
            
        if not isinstance(key,str):
            raise Exception('key must be a str')
        
        if self.r.exists(key):
            url = self.r.get(key)
            self.r.delete(key)
            return url
        else:
            return None
            
    pass
