from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow,getCurrentUserId,dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from bson import ObjectId
from api.lib.outletLib import OutletLib
from datetime import datetime

import os
import base64
import pandas as pd



@apiV1.resource('/testpaper/skills/<lang_id>')
class TestPaperSkillsList(Resource):
    
    def __init__(self):
        self.create_fields = {}
    
    def get(self,lang_id):
        try:
            result = mongo.db.question_sets.find({'test_type':'skills'},{'test_type':1,'name':1,'type':1,'options':1})
            data = []
            for row in result:
                row['read'] = 0
                data.append(getRow(row))
                
            return data,200 
        except:
            return {'error':{"message":"Something Wrong."}},400
    
    
        
@apiV1.resource('/testpaper/eLearning')
class TestPaperElearningList(Resource):
    
    def __init__(self):
        self.create_fields = {}
    
    def get(self):
        try:
            result = mongo.db.question_sets.find({'test_type':'eLearning'},{'test_type':1,'name':1,'type':1,'options':1})
            data = []
            for row in result:
                row['read'] = 0
                data.append(getRow(row))
                
            return data,200 
        except:
            return {'error':{"message":"Something Wrong."}},400   
        
        



@apiV1.resource('/testpaper/broadcast/<id>')
class TestPaperBroadcastList(Resource):
    
    def __init__(self):
        self.create_fields = {}
    
    #user id
    def get(self,id):
        try:
            result = mongo.db.broadcast_users.find({'user_id':getId(id),'read':0})
            
            data = []
            for r in result:
                result = mongo.db.broadcast_questions.find({'_id':r['broadcast_questions_id']})
                
                for row in result:
                    #row['read'] = 0
                    t = {}
                    t['id'] = str(r['_id'])
                    t['test_type'] = row['test_type']
                    t['name'] = row['name']
                    t['type'] = row['type']
                    t['options'] = [row['option1'],row['option2'],row['option3'],row['option4']]
                    t['read'] = row['read']
                    data.append(t)
            
            return data,200
            
        except:
            return {'error':{"message":"Something Wrong."}},400 
    
    #broadcast_users  id        
    def put(self,id): 
        try:
            user_id = getCurrentUserId()
            
            json = request.get_json()
            quetionId = getId(json['questionId'])
            answers = json['ansList']
            
            result = mongo.db.broadcast_users.update({'_id':getId(id)},{"$set":{'answers':answers,'read':1,'answered_at':datetime.now()}})
            return {'status':'Ok'},200
        except:
            return {'error':{"message":"Something Wrong."}},400        
    
 
 
 
 
 
    
@apiV1.resource('/testpaper/answer/<id>')
class TestPaperAnswer(Resource):
    
    def __init__(self):
        self.create_fields = {'title': {'type': 'string','empty': False,'required':True},
                              'url': {'type': 'string','empty': False,'required':True},
                              'type': {'type':'string','required':True,'allowed': ['video','document','image','url']}}
  
    def get(self,id):
        try:
            
            #result = mongo.db.broadcast_questions.update({'read':0})    
            return {'status':'ok'},200 
        except:
            return {'error':{"message":"Something Wrong."}},400
        
        
    def post(self,id):
        try:
            temp = {}
            
            
                
            return {'status':'ok'},200 
        except:
            return {'error':{"message":"Something Wrong."}},400            
        
      
        