from flask_socketio import emit, join_room, leave_room
from .. import socketio
from flask_jwt_extended import verify_jwt_in_request,get_jwt_identity
from flask import  request


from api import app, mongo
from api.lib.helper import getId
from datetime import datetime
import uuid
import time
from pyfcm import FCMNotification


def __sendPushNotification(registration_id,message_title,message_body):
        # Send to single device.
    push_service = FCMNotification(api_key="AAAAfq2WvOs:APA91bE2viBlyAy5eFQcAvT23YRkPFNLMByVp8txIzAWaR39KJCF0v2Dv0VEa9V_stGAs50Y7b-rIz-Cv_Jk1LIeY5cGscl3Axlpi9cBAiJfOkMcT2T8evRO9qcb13pXEdpZBDHpovYu")
    
    #print(registration_id)
    #print(message_title)
    #print(message_body)
    #registration_id = "cLx8jCMxVJA:APA91bHvrD_HnTNV2ImW43IWrjU6pEI4e1LMtUUExvhKhbmu4TuLZ6Bav779PT9sZncc01fMBTBoO0hBpneLEQ8akdudoc3T_jPv61Oa1WabPHO8zOgZ4HyvzNvSm7iCzol95tqAggNJ"
    #message_title = "Uber update"
    #message_body = "Hi john, your customized news for today is ready"
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
    
    #print(result)



def __sendBroadcastMessage(messageId,to_user_id,message,sent_at):
    #print("broadcast......")
    from_user_id = get_jwt_identity()
    #messageId = str(uuid.uuid4())
    #created_at = datetime.now()
    user = mongo.db.users.find_one({'_id':getId(from_user_id)})
    name = ''
    code = ''
    if(user):
        name = user['name']
        code = user['code']
        profile_pic = app.config['BASE_URL']+user['profile_pic']
    
    users = mongo.db.users.find({'parent_id':getId(to_user_id)})
    
    
    for row in users:        
        data = {'messageId':messageId,'from_user_id':from_user_id,'to_user_id':to_user_id,'name':name,'code':code,'profile_pic':profile_pic,'text':message,'sent_at':str(sent_at)}
        emit('message',data,room=to_user_id)
        
        sent_at = datetime.strptime(sent_at, '%Y-%m-%d %H:%M:%S')
        
        json = {'messageId':messageId,'from_user_id':getId(from_user_id),'to_user_id':row['_id'],'text':message, 'broadcast':1, 'sent_at':sent_at,'delivered_at':None}
        mongo.db.chat_history.insert(json)
        
        json = {'messageId':messageId,'from_user_id':getId(from_user_id),'to_user_id':row['_id'],'name':name,'code':code,'profile_pic':profile_pic,'text':message,'broadcast':1,'sent_at':sent_at,'delivered_at':None}
        mongo.db.chat_queue.insert(json)
        
        
    
def __sendMessage(messageId,to_user_id,message,sent_at,broadcast):
    
    from_user_id = get_jwt_identity()
    #messageId = str(uuid.uuid4())
    #created_at = datetime.now()
    user = mongo.db.users.find_one({'_id':getId(from_user_id)})
    name = ''
    code = ''
    registration_id = ''
    
    if(user):
        name = user['name']
        code = user['code']
        profile_pic = app.config['BASE_URL']+user['profile_pic']
        if "firebaseToken" in user:
            registration_id = user['firebaseToken']
            
    data = {'messageId':messageId,'from_user_id':from_user_id,'to_user_id':to_user_id,'name':name,'code':code,'profile_pic':profile_pic,'text':message,'broadcast':broadcast,'sent_at':str(sent_at)}
    
    __sendPushNotification(registration_id,name,message)
    
    emit('message',data,room=to_user_id)
    
    sent_at = datetime.strptime(sent_at, '%Y-%m-%d %H:%M:%S')
    json = {'messageId':messageId,'from_user_id':getId(from_user_id),'to_user_id':getId(to_user_id),'text':message,'broadcast':broadcast,'sent_at':sent_at,'delivered_at':None}
    mongo.db.chat_history.insert(json)
    json = {'messageId':messageId,'from_user_id':getId(from_user_id),'to_user_id':getId(to_user_id),'name':name,'code':code,'profile_pic':profile_pic,'text':message,'broadcast':broadcast,'sent_at':sent_at,'delivered_at':None}
    mongo.db.chat_queue.insert(json)
    
    


def __sendStatus(data):
    from_user_id = get_jwt_identity()
    #messageId = str(uuid.uuid4())
    #data['messageId'] = messageId
    emit('status',data,room=from_user_id)


def __sendQueue(to_user_id):
    try:
        result = mongo.db.chat_queue.find({'to_user_id':getId(to_user_id)})
        for row in result:
            data = {'messageId':row['messageId'],'from_user_id':str(row['from_user_id']),'to_user_id':str(row['to_user_id']),'name':str(row['name']),'code':str(row['code']),'profile_pic':str(row['profile_pic']),'text':row['text'],'broadcast':row['broadcast'], 'sent_at':str(row['sent_at'])}
            emit('message',data,room=to_user_id)
            
            
    except Exception as e:
        print(e)
    
def __deleteQueue(messageId):
    try:
        mongo.db.chat_queue.delete_one({'messageId':messageId})   
    except Exception as e:
        print(e)
    
@socketio.on('connect',namespace='/chat')
def connect():
    try:
        verify_jwt_in_request()
        from_user_id = get_jwt_identity()
        #print(request.sid)
        #print("You are connected : " + str(from_user_id))
        join_room(from_user_id)
        time.sleep(1)
        __sendStatus({'type':'Connected','text':"You are connected : " + str(from_user_id)})
        __sendQueue(from_user_id)
        
    except Exception as e:
        print(e)


@socketio.on('disconnect',namespace='/chat')
def disconnect():
    try:
        verify_jwt_in_request()
        from_user_id = get_jwt_identity()
        leave_room(from_user_id)
        __sendStatus({'type':'Disconnected','text':"You are disconnected : " + str(from_user_id)})
    except Exception as e:
        print(e)

      
@socketio.on('status',namespace='/chat')
def status(data):
    try:
        verify_jwt_in_request()
        #print(data)
        if data['type'] == 'Received':
            receive_at = datetime.strptime(data['receive_at'], '%Y-%m-%d %H:%M:%S')
            myquery = {'messageId':data['messageId']}
            newvalues = {"$set": {'delivered_at':receive_at}}
            mongo.db.chat_history.update_one(myquery,newvalues)
            __deleteQueue(data['messageId'])

    except Exception as e:
        print(e)


@socketio.on('message',namespace='/chat')
def message(data):
    try:
        verify_jwt_in_request()
        
        if 'broadcast' in data and int(data['broadcast']) == 1:
            __sendBroadcastMessage(data['messageId'],data['to_user_id'], data['text'],data['sent_at'])
            __sendMessage(data['messageId'],data['to_user_id'], data['text'],data['sent_at'],1)
        else:        
            __sendMessage(data['messageId'],data['to_user_id'], data['text'],data['sent_at'],0)
            
        __sendStatus({'type':'Received','messageId':data['messageId'],'receive_at':str(datetime.now()),'text':'Message Received'})
    
    except Exception as e:
        print(e)
 
        


  