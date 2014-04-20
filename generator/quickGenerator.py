#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
exec_path = os.path.abspath(os.path.dirname(__file__)).rsplit("/",1)[0]
conf_path = exec_path+"/common/config.json"

import sys
sys.path.insert(0,exec_path)

from common import auth_api, model
from common import readReplyTable
import reply
# 解析結果に基づいて文章生成(または行動を起こす)
#import model
#import scheduler
import datetime
#from sqlalchemy import and_
import random
import string
import sys
import simplejson
import re
from tweepy.error import TweepError


def quickGenerate():
    #sched = scheduler.Scheduler()
    #sched.schedule()
    u = LoadUserData(conf_path)
    table, footer= readReplyTable.read(exec_path+"/common/replyTable.json")
    dbSession = model.startSession(u)
    if False:
        if( sched.has_schedule() ):
            str = doSchedule(sched)
    else:
        rep = dbSession.query(model.RetQueue)
        if( rep.count() > 0 ):
            str, reply_id = reply.do(table, rep,dbSession)
            sendMessage(str,reply_id)
    dbSession.close()


def LoadUserData(fileName):
    #ファイルを開いて、データを読み込んで変換する
    #データ形式は(user,password)
    try:
        file = open(fileName,'r')
        a = simplejson.loads(file.read())
        file.close()
    except IOError:
        print "IOError"
        sys.exit(1)
    return a


# Twitterにメッセージ投げる
def sendMessage(str, reply_id):
    userdata = LoadUserData(conf_path)
    tw = auth_api.connect(userdata["consumer_token"],
        userdata["consumer_secret"], exec_path+"/common/")
    str = string.replace(str,'yystart','')
    str = string.replace(str,'yyend','')
    
    try:
        tw.update_status(str, reply_id)
    except TweepError,e:
        reg = re.compile('^\[{\'message\': \'(.+)\', \'code\': (\d+)}\]$')
        mat = reg.match(e.reason)
        if mat:
            code = mat.group(2)
            if code == '187':
                print 'status duplicate'
                return
        raise

if __name__ == "__main__":
	quickGenerate()
