#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wsgiref.handlers import CGIHandler
import sys


ourpeer_id=2000000001#peer_id  chata
mychat_id=51#id chata admina
coins=0
owner_id='-153796220'#id паблика
coll_to_vote=6
from flask import Flask, request, json,render_template, escape, redirect, jsonify,json
import settings
import vk
import MySQLdb
import re
import asyncio
import threading
import time



    


def votecal(data,mes):
    sessiondata=mes.split(' ')
   
    if len(sessiondata)!=3:
        #print('error 1')
        return 'error vote'
        
    result=re.search(r'\[(id\w*)\|(\w*)\]',sessiondata[1])
    if result==None:
        #print('error2')
        return 'error vote'
    number=re.search(r'^\d+$',sessiondata[2])
    if result==None:
        #print('error3')
        return 'error vote'
    
    session = vk.Session()
    api = vk.API(session, v='5.80')
    peer_id = data['object']['peer_id']
    votedata=api.polls.create(access_token=settings.token,question='Начислить '+sessiondata[1].split('|')[1][:len(sessiondata[1].split('|')[1])-1]+'('+sessiondata[1].split('|')[0][1:]+') '+sessiondata[2]+' ШК',add_answers=json.dumps(["да", "нет"]))
    post_id=api.wall.post(owner_id=owner_id, access_token=settings.mytoken,attachments='poll'+str(votedata['owner_id'])+'_'+str(votedata['id']),from_group='1')
    api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',attachment='wall'+'-153796220'+'_'+str(post_id['post_id'])+'_'+settings.pubtoken)
    fff=votedata['id']
    fff2=votedata['owner_id']
    fff3=sessiondata[2]
    fff4=sessiondata[1].split('|')[0][3:]
    name=sessiondata[1].split('|')[1][:len(sessiondata[1].split('|')[1])-1]
    postid=post_id['post_id']
    try:
        conn = MySQLdb.connect(host="185.241.54.179", user="root",
                           passwd="samuel2205", db="site",charset='utf8')
        cursor = conn.cursor()
        
    except MySQLdb.Error as err:
        api.messages.send(access_token=settings.pubtoken, peer_id=str(data['object']['peer_id']),v='5.80',message='Ошибка подключения к базе')
        #print("Connection error: {}".format(err))
        conn.close()
        return 'er'
    mytime=0
    sql = """INSERT INTO gol(idofpoll,owner,votecoins,vote_user_id,peer_id,name,postid,mytime)
        VALUES ('%(idofpoll)s', '%(owner)s', '%(votecoins)s', '%(vote_user_id)s', '%(peer_id)s', '%(name)s', '%(postid)s','%(mytime)s')
        """%{"idofpoll":fff, "owner":fff2, "votecoins":fff3, "vote_user_id":fff4, "peer_id":peer_id, "name":name, "postid":postid,"mytime":mytime}
        # исполняем SQL-запрос
    cursor.execute(sql)
    
        # применяем изменения к базе данных
    conn.commit()
    conn.close()


def balancecheck(data):
    session = vk.Session()
    api = vk.API(session, v='5.80')
    balance_user_id=data['object']['from_id']
    peer_id=data['object']['peer_id']
    try:
        conn = MySQLdb.connect(host="185.241.54.179", user="root",passwd="samuel2205", db="site")
        cursor = conn.cursor()
    except MySQLdb.Error as err:
        #print("Connection error: {}".format(err))
        conn.close()
        return 'er'
    sql = """select coins,shtr from users3 where user_id=%(user_id)s
        """%{"user_id":balance_user_id}
    cursor.execute(sql)
    result = cursor.fetchall()
    #print(result)
        # применяем изменения к базе данных
    conn.commit()
    conn.close()
    api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',message='Штрафкоинов = '+str(result[0][0])+' Штрафных  = '+str(result[0][1]))
    return 'ok'


def shtraf(data,mes):
    session = vk.Session()
    api = vk.API(session, v='5.80')    
    sessiondata=mes.split(' ')
    peer_id = data['object']['peer_id']
    balance_user_id=data['object']['from_id']
    if len(sessiondata)!=2:
        #print('error 1')
        return 'error vote'
        
    result=re.search(r'\[(id\w*)\|(\w*)\]',sessiondata[1])
    if result==None:
        #print('error2')
        return 'error vote'

    try:
        conn = MySQLdb.connect(host="185.241.54.179", user="root",passwd="samuel2205", db="site")
        cursor = conn.cursor()
        
    except MySQLdb.Error as err:
        #print("Connection error: {}".format(err))
        conn.close()
        return 'er'
    sql = """select coins from users3 where user_id=%(user_id)s
        """%{"user_id":balance_user_id}
    cursor.execute(sql)
    result = cursor.fetchall()
    if result[0][0]<7:
        api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',message='Мало штрафкоинов')
        return 'error'
    sql = """UPDATE users3 set coins=coins-7 where user_id =%(user_id)s 
        """%{"user_id":balance_user_id}
    cursor.execute(sql)
    sql = """UPDATE users3 set shtr=shtr+1 where user_id =%(user_id)s 
        """%{"user_id":sessiondata[1].split('|')[0][3:]}
    cursor.execute(sql)
    conn.commit()
    conn.close()
    api.messages.send(access_token=settings.pubtoken, peer_id=str(peer_id),v='5.80',message='Пользователю '+ sessiondata[1] + ' прописана штрафная!' )
    return 'ok'




template_path = os.path.join(os.path.dirname(__file__), 'templates')
app = Flask(__name__, template_folder=template_path)
@app.route('/', methods=['POST'])

def processing():

    #Распаковываем json из пришедшего POST-запроса
    data = json.loads(request.data)
    session = vk.Session()
    api = vk.API(session, v='5.80')   
    #Вконтакте в своих запросах всегда отправляет поле типа
    if 'type' not in data.keys():
        return 'not vk'
    elif data['type'] == 'confirmation':
        return '65e6bc7f'
    elif data['type'] == 'message_new':
        if  'action' in  data['object']:
            if data['object']['action']['type']=='chat_invite_user':
                return 'ok' #newuser(data['object']['action']['member_id'])
            else:
                return 'ok'

        elif 'text' in data['object']:
            mes=data['object']['text']
            result=re.match(r'^(!vote)',mes)
            if result!=None:
                votecal(data,mes)
                #api.messages.send(access_token=settings.pubtoken, peer_id=str(data['object']['peer_id']),v='5.80',message='Тут типа выход из голосование '+ mes )
                return 'ok'
            else:
                result=re.match(r'^(!баланс)$',mes)
                if result!=None:
                    balancecheck(data)
                    return 'ok'
                else:
                    result=re.match(r'^(!штрафная)',mes)
                    if result!=None:
                        shtraf(data,mes)
                        return 'ok'
                    else:
                        #print('Новое сообщение '+ mes)
                        return 'ok'
        else:
            return 'ok'

    else:
        return 'нет обработчика'
    

CGIHandler().run(app)

