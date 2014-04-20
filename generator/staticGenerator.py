#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
exec_path = os.path.abspath(os.path.dirname(__file__)).rsplit("/",1)[0]
conf_path = exec_path+"/config.json"

import sys
sys.path.insert(0,exec_path)

from common import twitterscraping
import reply
# 解析結果に基づいて文章生成(または行動を起こす)
import model
#import scheduler
import datetime
#from sqlalchemy import and_
import random
import string
import sys
import simplejson

def staticGenerate():
    #sched = scheduler.Scheduler()
    #sched.schedule()
    u = LoadUserData(conf_path)
    dbSession = model.startSession(u)
    if False:
        if( sched.has_schedule() ):
            str = doSchedule(sched)
    else:
        q = dbSession.query(model.Condition)
        q2 = q.filter(model.Condition.name=="hunger")
        if q.count() == 0:
            c = model.Condition()
            c.name = "hunger"
            c.value ="1000"
            dbSession.save(c)
            dbSession.commit()
        else:
            cond = q2.one().value
            print cond
            sendMessage( u"おなかすいたー" )
        """if( rep.count() > 0 ):
            str = reply.do(rep,dbSession)
            sendMessage(str)
        """

def LoadUserData(fileName):
    #ファイルを開いて、データを読み込んで変換する
    #データ形式は(user,password)
    try:
        file = open(fileName,'r')
        a = simplejson.loads(file.read())
        file.close()
    except:
        sys.exit(1)
    return a


# Twitterにメッセージ投げる
def sendMessage(str):
    userData = LoadUserData(conf_path)
    tw = twitterscraping.Twitter(userData)
    str = string.replace(str,'yystart','')
    
    #print(str)
    tw.put(str)

if __name__ == "__main__":
	staticGenerate()
