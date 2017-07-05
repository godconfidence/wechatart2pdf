# -*- coding: utf-8 -*-

import MySQLdb


class MysqlUtil(object):

    def __init__(self):
        self.conn = MySQLdb.connect("182.92.123.81", "root", "B2WKE$K-R9V3BMEM=UM)P", "wxarticle", 3306)
        self.conn.set_character_set('utf8')
        self.cur = self.conn.cursor()
    pass
    
    
    def select(self,sql):

        #获得表中有多少条数据
        aa = self.cur.execute(sql)
        if aa == 0:
            self.close()
            return (aa,None)
        else:
            info = self.cur.fetchmany(aa)
            self.close()
            return (aa,info)

    pass


    def executemany(self,sqli,sql_list):
        
        self.cur.executemany(sqli, sql_list)
        self.close()
        
    pass


    def execute_no_query(self,sqli):
        
        self.cur.execute(sqli)
        self.close()
        
    pass


    def close(self):

        """
        关闭数据库链接

        """

        try:

            self.cur.close()
            self.conn.commit()
            self.conn.close()

        except Exception as identifier:

            pass
        pass

    pass
    