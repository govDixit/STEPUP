from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getRow,getId,getCurrentUserId, dateTimeValidate,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
import urllib
import uuid


@apiV1.resource('/learning/download/<filename>')
class LearningDownload(Resource):
    def get(self,filename):
        try:
            path = "../"+app.config['UPLOAD_FOLDER']+'learning/'+filename
            #print(path)
            return send_file(path, as_attachment=True)
        except Exception as e:
            return {'error':{"message":str(e)}},400
        
        
# This is for Web
@apiV1.resource('/web/learning')
class eLearningList(Resource):
   
    def __init__(self):
        self.create_fields = {'role': {'type': 'number','required': True,'allowed': [1,2,3]},
                              'title': {'type': 'string','required': True,'empty': False},
                              'type': {'type': 'string','required': True,'empty': False},
                              'url': {'type': 'string','required': True,'empty': False},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            
            result = mongo.db.skills_lang.find()
            
            if search != 'null' and search != '':
                result = mongo.db.eLearning.find({'title':{'$regex' : search, '$options' : 'i'}}).skip(start).limit(length)
            else:
                result = mongo.db.eLearning.find().skip(start).limit(length)
                
            total = result.count()
            
            temp = []
            for row in result:
                temp.append(getRow(row))
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
                
                if json['type'] == 'document':
                    file = json['url'] 
                    filename = self.saveFile(file)
                    del json['url']
                    if not filename:
                        return {'error':{"message":"File is not a valid"}},400
                    json['url'] = filename
                
                
                json['created_at'] = datetime.now()
                id = mongo.db.eLearning.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["Already exist."]}},400
        
        
    def saveFile(self,file):
        try:
            filename = file.split(',')[0]
            filetype = filename.replace("data:",'').replace(";base64","")
            filetype = filetype.split('/')[1]
            
            response = urllib.request.urlopen(file)
            
            unique_filename = str(uuid.uuid4())
            newFilename = unique_filename+"."+filetype
            
            path = app.config['UPLOAD_FOLDER']+"learning/"+newFilename
           
            with open(path, 'wb') as f:
                f.write(response.file.read())
                
            return newFilename
        except:
            return False
        
 
 
 
 
 
        
@apiV1.resource('/learning')
class Learning(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'title': {'type': 'string','empty': False,'required':True},
                              'url': {'type': 'string','empty': False,'required':True},
                              'type': {'type':'string','required':True,'allowed': ['video','document','image','url']}}
  
    def get(self):
        try:
            result = mongo.db.eLearning.find()
            data = []
            user_id = getId(getCurrentUserId())
            
            docs = self.getDocIds(user_id)
            
            for row in result:
                if row['type'] == 'document':
                    row['url'] = app.config['DOC_URL']+ "learning/download/"+row['url']
                row['read'] = 0
                
                if str(row['_id']) in docs:
                    row['read'] = 1
                
                data.append(getRow(row))
                
            return data,200 
        except:
            return {'error':{"message":"Something Wrong."}},400
        
    
    
    def getDocIds(self,user_id):
        try:
            result = mongo.db.user_learning.find_one({'user_id':user_id})
            docs = {}
            if result:
                for doc in result['docs']:
                    docs[str(doc)] = 1
                    
            return docs
        except:
            return {}
    
        
    def post(self,lang_id):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            temp = request.get_json()
            
            if v.validate(temp):
                json = {}
                json['title'] = temp['title']
                json['url'] = temp['url']
                json['type'] = temp['type']
                json['status'] = 1
                json['created_at'] = datetime.now()
                
                id = mongo.db.eLearning.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["Language exist."]}},400
        
    
  
    

@apiV1.resource('/learning/read/<id>')
class LearningRead(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'title': {'type': 'string','empty': False,'required':True},
                              'url': {'type': 'string','empty': False,'required':True},
                              'type': {'type':'string','required':True,'allowed': ['video','document','image','url']}}
  
    def get(self,id):
        try:
            temp = {}
            temp['user_id'] = getId(getCurrentUserId())
            temp['docs'] = []
            temp['created_at'] = datetime.now()
            
            result = mongo.db.user_learning.find_one({'user_id':temp['user_id'],'docs':getId(id)})
            
                
            return {'status':'ok'},200 
        except:
            return {'error':{"message":"Something Wrong."}},400
        
        
    def post(self,id):
        try:
            temp = {}
            temp['user_id'] = getId(getCurrentUserId())
            temp['docs'] = []
            temp['created_at'] = datetime.now()
            
            result = mongo.db.user_learning.find_one({'user_id':temp['user_id']})
            if not result:
                mongo.db.user_learning.insert(temp)
                  
            myquery = {'user_id':temp['user_id'],"docs.id":getId(id)}
            myquery = {'user_id':temp['user_id']}
            newvalues = {"$addToSet": {"docs":getId(id)}}
            mongo.db.user_learning.update_one(myquery,newvalues)  
            
                
            return {'status':'ok'},200 
        except:
            return {'error':{"message":"Something Wrong."}},400            
        
  
