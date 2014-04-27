#!/usr/bin/env python
# -*- coding: utf-8 -*-

# analyzerのうちの単純応答だけ高速に出す
# 1min程度cronで
# 最初過去時間は1min固定->lastUpdateに
import os
import mecab
import datetime
import re
import sys
from sqlalchemy import and_

import picklefile
import simplejson
mecabPath = "/usr/lib/libmecab.so.1"
g_mecabencode = g_systemencode = "utf-8"
g_outencode = g_systemencode
_debug = False 
homepath = os.path.abspath(os.path.dirname(__file__)).rsplit("/",1)[0]
exec_path = homepath
conf_path = exec_path+"/common/config.json"

import sys
sys.path.insert(0,exec_path)

from common import readReplyTable, model

dbSession = None

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


def quickAnalyze():
    # dbからデータを読み込む
    u = LoadUserData(conf_path)
    dbSession = model.startSession(u)
    table, footer = readReplyTable.read(exec_path + "/common/replyTable.json")
    regexes = makeRegexes(table)
    
    # 前回の更新時間から現在までのデータを入手する
    q = dbSession.query(model.Tweet)
    tq = q.filter(model.Tweet.isAnalyze == 0)[:10000]
    for t in tq:
        #1発言毎
        t.text = RemoveCharacter(t.text)
        #print_d2(t.text)
        analyzeReply2(t,dbSession,table,regexes)
        t.isAnalyze = 1
        t_enc = t.text.encode(g_mecabencode,'ignore')
        sarray = mecab.sparse_all(t_enc,mecabPath).split("\n")
        sarray2 = connectUnderScore(sarray)
        markovWordList,topNWordList = TakeWordList(sarray)
        
        #最近出た名詞貯める
        for tn in topNWordList:
            hot = model.Hot()
            hot.word = unicode(tn,g_systemencode)
            dbSession.add(hot)
        dbSession.add(t)
        dbSession.commit()
    dbSession.close()

# A,_,B->A_Bに直す
def connectUnderScore(array):
    retArray = []
    i = 0
    while(i < len(array)-2):
        if array[i+1] == "_":
            retArray.append(array[i] + "_" + array[i+2])
            i+=3
        else:
            retArray.append(array[i])
        i+=1
    #print i
    if(i < len(array)):retArray.append(array[i])
    if(i+1 < len(array)):retArray.append(array[i+1])
    return retArray        


# 分解した品詞列から単語群と重要単語を抜き出す
def TakeWordList(sarray):    
    markovWordList = []
    topNWordList = []
    for sa in sarray:
        if sa.startswith("EOS") : break
        sa2 = sa.split("\t")
        sa2[0] = unicode(sa2[0],g_mecabencode,'ignore').encode(g_systemencode,'ignore')
        print_d2(sa2[0])
        #markovWordList.append(sa2[0])
        sa3 = sa2[1].split(",")
        if unicode(sa3[0],g_mecabencode) == u"名詞" :
            if unicode(sa3[1],g_mecabencode) == u"固有名詞" or \
                unicode(sa3[1],g_mecabencode) == u"一般":
                if sa2[0] != "yystart" and sa2[0] != "yyend":
                    topNWordList.append(sa2[0])
    return markovWordList,topNWordList


# test内容
# RemoveCharacter("検索サイト http://www.google.com")->検索サイト
# RemoveCharacter("検索サイト [mb]")->検索サイト
# RemoveCharacter("検索サイト *Tw*")->検索サイト
# しかしこれcrawlerでやるべきだよなぁ
def RemoveCharacter(str):
    #余計な記号(http://とか、[hoge]とか)
    reg = re.compile('http://\S+\s*')
    regTag = re.compile('[.*]')
    regTag2 = re.compile('\*.*\*')

    if reg.search(str):
        print_d2("http cut")
        str = reg.sub(' ',str)
    
    if regTag.search(str):
        print_d2("tag cut")
        str = regTag.sub(' ',str)

    if regTag2.search(str):
        print_d2("tag2 cut")
        str = regTag2.sub(' ',str)

    return str


def print_d2(str):
    if _debug:
        print unicode(str,g_systemencode,'ignore').encode(g_outencode,'ignore'),


def CheckTime(type,timespan,x,d,session):
    replyFlag = False
    ot = None
    q = session.query(model.OhayouTime).filter(and_(model.OhayouTime.user == x.user,model.OhayouTime.type == type))
    if q.count() > 0:
        ot = q[0]
        if datetime.datetime.today() - ot.datetime > timespan:
            replyFlag = True
        else:
            pass
    else:
        replyFlag = True

    if replyFlag:
        d.user = x.user
        d.text = type
        d.reply_id = x.tweetID
        if ot == None:
            ot = model.OhayouTime()
            ot.user = d.user
            ot.type = d.text
        ot.datetime=datetime.datetime.today()
        session.add(ot)
    return d


def makeRegexes(table):
    regexes = {}
    for key, t in table.iteritems():
        regexes[key] = re.compile(t[3])
    return regexes


def analyzeReply2(x, session, table, regexes):
    d = model.RetQueue()
    d.user = ""

    for key, regOne in regexes.iteritems():
        if regOne.search(x.text):
            print_d2(key+" hit")
            if key == "at":
                d.user = x.user
                text = re.sub("@\S* ","",x.text)
                d.text = u"at"+text
                d.reply_id = x.tweetID
            else:
                if table[key][2] > 0:
                    CheckTime(key,datetime.timedelta(minutes=table[key][2]),x,d,session)
                else:
                    d.user = x.user
                    d.text = key
                    d.reply_id = x.tweetID

            break
    if( d.user != "" ):
        print "append", d.user
        session.add(d)
    session.commit()
    #@がきた時の応答はあとで考える(自動学習させる)


if __name__ == "__main__":
    quickAnalyze()
