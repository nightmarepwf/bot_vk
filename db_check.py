#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import settings
import vk
import MySQLdb
import re
import time
ourpeer_id=2000000001#peer_id  chata
mychat_id=51#id chata admina
coins=0
owner_id='-153796220'#id паблика
coll_to_vote=6

def votecheck(idofpoll,owner,votecoins,vote_user_id,peer_id,name,postid,mytime):
    session = vk.Session()
    api = vk.API(session, v='5.80')
    poll_data=api.polls.getById(access_token=settings.token,v='5.80',owner_id=owner,is_board=0,poll_id=idofpoll)
    if (int(poll_data['answers'][0]['votes'])+int(poll_data['answers'][1]['votes'])<coll_to_vote) and mytime<120 :
        try:
            conn = MySQLdb.connect(host="185.241.54.179", user="root",
                           passwd="samuel2205", db="site")
            cursor = conn.cursor()
        except MySQLdb.Error as err:
            conn.close()
        sql = """UPDATE gol set mytime=mytime+1 where postid =%(postid)s 
        """%{"postid":postid}
        cursor.execute(sql)
        # применяем изменения к базе данных
        conn.commit()
        conn.close()
        return 'no time'
    session = vk.Session()
    api = vk.API(session, v='5.80')
    poll_data=api.polls.getById(access_token=settings.token,v='5.80',owner_id=owner,is_board=0,poll_id=idofpoll)
    if int(poll_data['answers'][0]['votes'])+int(poll_data['answers'][1]['votes'])<coll_to_vote:
        api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',message='Мало проголосовавших')
        api.wall.delete(access_token=settings.token,v='5.80',owner_id=owner_id,post_id=postid)
        try:
            conn = MySQLdb.connect(host="185.241.54.179", user="root",
                           passwd="samuel2205", db="site")
            cursor = conn.cursor()
        except MySQLdb.Error as err:
            conn.close()
            return 'er'
        sql = """delete from gol where postid =%(postid)s 
        """%{"postid":postid}
        cursor.execute(sql)
        # применяем изменения к базе данных
        conn.commit()
        conn.close()        
        #Голосование завершено , слишком мало проголосовавших
        return 'ok'
    if float(poll_data['answers'][0]['rate'])<=50:
        api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',message='Больше половины против')
        api.wall.delete(access_token=settings.token,v='5.80',owner_id=owner_id,post_id=postid)
        try:
            conn = MySQLdb.connect(host="185.241.54.179", user="root",
                           passwd="samuel2205", db="site")
            cursor = conn.cursor()
        except MySQLdb.Error as err:
            conn.close()
            return 'er'
        sql = """delete from gol where postid =%(postid)s 
        """%{"postid":postid}
        cursor.execute(sql)
        # применяем изменения к базе данных
        conn.commit()
        conn.close()   
        #Голосование завершено , большинство против
        return 'ok'
        
    try:
        conn = MySQLdb.connect(host="185.241.54.179", user="root",
                           passwd="samuel2205", db="site")
        cursor = conn.cursor()
    except MySQLdb.Error as err:
        conn.close()
        return 'er'
    sql = """UPDATE users3 set coins=coins+%(coins)s where user_id =%(user_id)s 
        """%{"coins":votecoins,"user_id":vote_user_id}
        # исполняем SQL-запрос
    cursor.execute(sql)
        # применяем изменения к базе данных
    sql = """delete from gol where postid =%(postid)s 
        """%{"postid":postid}
    cursor.execute(sql)
    conn.commit()
    conn.close()
    api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',message='Пользователю ' + str(name) +' зачислено '+str(votecoins)+ ' ШК ' )
    api.wall.delete(access_token=settings.token,v='5.80',owner_id=owner_id,post_id=postid)
    #print(poll_data)
    #print('прошло 60 секунд с начала голосования!')
    return 'ok'

i=0
while i<999999:
    time.sleep(60)
    try:
        conn = MySQLdb.connect(host="185.241.54.179", user="root",
                           passwd="samuel2205", db="site",charset='utf8')
        cursor = conn.cursor()
    except MySQLdb.Error as err:
        print('error')
        conn.close()
        api.wall.delete(access_token=settings.token,v='5.80',owner_id=owner_id,post_id=postid)

    sql = """Select * from gol 
        """
        # исполняем SQL-запрос)
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit() # применяем изменения к базе данных
    conn.close()
    for db_date in result:
        votecheck(db_date[0],db_date[1],db_date[2],db_date[3],db_date[4],db_date[5],db_date[6],db_date[7])
        

    
