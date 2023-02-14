from flask import session
from flask_socketio import emit, join_room, leave_room
from .. import socketio
import time
from datetime import datetime
import uuid
from app import mongo


def getPriority():
            
    user_id = str(session['user_id'])
    result = mongo.db.miform.find_one({"user_id":user_id})
    if result:
        myquery = {"user_id":user_id}
        newvalues = {"$inc": {"priority": int(1)} }
        #mongo.db.miform.update_one(myquery, newvalues)
  
        return result['priority'];
    else:
        mongo.db.miform.insert({'user_id':user_id,'created_at':datetime.now(),'priority':1})
        return 1



def __sendMessage():
    priority = getPriority();
    #print(priority)
    result = mongo.db.form_fields.find_one({'priority':priority})
    #print(result)
    messageId = str(uuid.uuid4())
    
    currentDT = datetime.now()
    sent_at = currentDT.strftime("%I:%M %p")
    
    data = {}
    if result:
        result.pop('_id') 
        data = {'messageId':messageId,'question':result,'sent_at':str(sent_at)+', Today'}
    else:
        default_data = {
            "label" : "Bye ...",
            "type" : "input",
            "priority" :0,
            "status" : 1
        }
        data = {'messageId':messageId,'question':default_data,'sent_at':str(sent_at)+', Today'}
    
    user_id = str(session['user_id'])
    emit('message',data,room=user_id)
    
    
    
      
def __sendStatus(data):
    user_id = str(session['user_id'])
    emit('status',data,room=user_id)
    
       

@socketio.on('message',namespace='/')
def message(data):
    try:
        try:
            user_id = str(session['user_id'])
            myquery = {"user_id":user_id}
            newvalues = {"$inc": {"priority": int(1)}, "$addToSet": {"result":{'question':data['question'],"answer":data['text']}}}
            mongo.db.miform.update_one(myquery, newvalues)
        except Exception as e:
            print(e)
        
        __sendMessage()
        #__sendStatus({'type':'Received','messageId':data['messageId'],'receive_at':str(datetime.now()),'text':'Message Received'})
    except Exception as e:
        print(e)
        
 
    

@socketio.on('connect',namespace='/')
def connect():
    try:
        #print(request.sid)
        print("You are connected : " + str(session['user_id']))
        
        join_room(session['user_id'])
        time.sleep(1)
        __sendStatus({'type':'Connected','text':"You are connected : " + str(session['user_id'])})
        __sendMessage()
        
    except Exception as e:
        print(e)


@socketio.on('disconnect',namespace='/')
def disconnect():
    try:
        leave_room(session['user_id'])
        __sendStatus({'type':'Disconnected','text':"You are disconnected : " + str(session['user_id'])})
    except Exception as e:
        print(e)



