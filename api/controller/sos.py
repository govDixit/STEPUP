from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUserId, dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta


@apiV1.resource('/sos')
class SOSNotification(Resource):
    
    def __init__(self):
        self.create_fields = {'date': {'type': 'date','empty': False,'required':True},
                              'coardinates': {'type': 'dict',
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
  
    def get(self):
        try:
            
            result = mongo.db.sos_notification.find()
            data = []
            for row in result:
                print(row)
            return getData(result),200 
        except:
            return {'error':{"message":"Something Wrong."}},400
        
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            json['date'] = dateTimeValidate(json['date'])
            if v.validate(json):
                json['user_id'] = getId(getCurrentUserId())
                json['coardinates']['latitude'] = float(json['coardinates']['latitude'])
                json['coardinates']['longitude'] = float(json['coardinates']['longitude'])
                json['read'] = 0
                
                id = mongo.db.sos_notification.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["SOS notification exist."]}},400
           

@apiV1.resource('/sos/<id>')
class SOSNotificationById(Resource):
    
    def __init__(self):
        self.create_fields = {'date': {'type': 'date','empty': False,'required':True},
                              'coardinates': {'type': 'dict',
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
  
    def get(self,id):
        try:
            aggr = [{"$lookup": { "from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"}]
            aggr.append({"$match":{"read":0}}) 
            result = mongo.db.sos_notification.aggregate(aggr)
            data = []
            for row in result:
                row['name'] = row['user']['name']
                row['code'] = row['user']['code']
                row['role'] = row['user']['role']
                row.pop('user')
                data.append(getData(row))
                
                
            return data,200 
        except:
            return {'error':{"message":"Something Wrong."}},400
        
    
    def put(self,id):
        try:
            result = mongo.db.sos_notification.update_one({'_id':getId(id)},{"$set": {'read':1}})
            return {'status':'ok'},200
        except:
            return {'error':{"message":"Something Wrong."}},400
        
        
        
        
        
             