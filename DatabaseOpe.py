# -*- coding: utf-8 -*-
"""
Created on Sat Feb  4 17:53:31 2017

@author: tomoya
"""
import sqlite3
import datetime

class DatabaseOpe:
    def __init__(self,DBpath):
        self.con = sqlite3.connect(DBpath, isolation_level=None)
        self.cur = self.con.cursor()

    def getProperty(self,name):
        self.cur.execute(self.getQuery('get_property'),(name,))
        return self.getNull(self.cur.fetchall())[0]

    def insertBlogs(self,seq,title,url,Text):
        self.cur.execute(self.getQuery('insertBlogs'),(seq,title,url,Text,self.getToday()))

    def getBlogs(self,url):
        self.cur.execute(self.getQuery('getBlogs'),(url,))
        return self.getNull(self.getNull(self.cur.fetchall()))

    def getBlogsSeq(self):
        self.cur.execute(self.getQuery('getBlogsSeq'))
        return self.getSeqInc(self.cur.fetchall()[0])

    # クエリ取得処理
    def getQuery(self,queryName):
        self.cur.execute("select query from query where query_name = ?",(queryName,))
        sql = self.cur.fetchall()[0]
        return sql[0]

    # シークエンスクリメント処理
    def getSeqInc(self,seq):
        seq = seq[0]
        if seq is None:
            seq = 1
        else:
            seq = seq + 1
        return seq

    # Null対策処理
    def getNull(self,data):
        if data is not None :
            if len(data) != 0:
                data = data[0]
            else :
                data = None
        return data

    # Null対策処理
    def getNulls(self,data):
        if len(data) != 0:
            data = data
        else :
            data = None
        return data

    # データリスト変換処理
    def getList(self,data):
        templist = []
        for temp in data:
            templist.append(temp[0])
        return templist

    # 有無判定
    def getBool(self,list,word):
        try:
            temp = list.index(word)
            temp = True
        except ValueError:
            temp = False
        return temp

    # 日時取得
    def getToday(self):
        today = datetime.datetime.today()
        today = today.strftime('%Y-%m-%d %H:%M:%S')
        return today
