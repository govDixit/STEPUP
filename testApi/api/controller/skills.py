from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getRow,getId,getCurrentUserId, dateTimeValidate, getCurrentUser
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
import urllib
import uuid
import jwt
from flask_jwt_extended import (
     get_jwt_identity
)


@apiV1.resource('/skills/download/<filename>')
class SkillsDownload(Resource):
    def get(self,filename):
        try:
            path = "../"+app.config['UPLOAD_FOLDER']+'skills/'+filename
            #print(path)
            return send_file(path, as_attachment=True)
        except Exception as e:
            return {'error':{"message":str(e)}},400
        


# This is for Web
@apiV1.resource('/skills')
class SkillsList(Resource):
   
    def __init__(self):
        self.create_fields = {'lang_id': {'type': 'string','required': True,'empty': False},
                              'role': {'type': 'number','required': True,'allowed': [1,2,3]},
                              'title': {'type': 'string','required': True,'empty': False},
                              'type': {'type': 'string','required': True,'empty': True},
                              'url': {'type': 'string','required': True,'empty': True},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            
            result = mongo.db.skills_lang.find()
            langs = {}
            for row in result:
                langs[str(row['_id'])] = row['name']
                
            
            if search != 'null' and search != '':
                result = mongo.db.skills.find({'title':{'$regex' : search, '$options' : 'i'}}).skip(start).limit(length)
            else:
                result = mongo.db.skills.find().skip(start).limit(length)
                
            total = result.count()
            
            temp = []
            for row in result:
                if str(row['lang_id']) in langs:
                    row['lang_id'] = langs[str(row['lang_id'])]
                else:
                    row['lang_id'] = 'None'
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
            #return json,200
            if v.validate(json):
                if json['type'] == 'document':
                    file = json['url'] 
                    filename = self.saveFile(file)
                    del json['url']
                    if not filename:
                        return {'error':{"message":"File is not a valid"}},400
                    json['url'] = filename
                    
                    
                json['lang_id'] = getId(json['lang_id'])
                json['created_at'] = datetime.now()
                id = mongo.db.skills.insert(json)
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
            
            path = app.config['UPLOAD_FOLDER']+"skills/"+newFilename
           
            with open(path, 'wb') as f:
                f.write(response.file.read())
                
            return newFilename
        except:
            return False   
        
        
@apiV1.resource('/skills/language')
class SkillsLanguage(Resource):
    
    def __init__(self):
        self.create_fields = {'name': {'type': 'string','empty': False,'required':True}}
  
    def get(self):
        current_user = getCurrentUser()
        # ~ app.logger.info(getCurrentUser())
        try:
            role = current_user['role']
            # ~ app.logger.info(role)
            if role != 3 and role !=1:
                return {'error' : {'message':'You don\'t have permission!'}}, 403
            else:
                result = mongo.db.skills_lang.find()
                return getData(result),200 
        except:
            return {'error':{"message":"Something Wrong."}},400
        
        
        
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
                json['status'] = 1
                json['created_at'] = datetime.now()
                
                id = mongo.db.skills_lang.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["Language exist."]}},400
        


@apiV1.resource('/skills/language/select')
class SkillsLanguageSelect(Resource): 
    def get(self):
        try:           
            result = mongo.db.skills_lang.find()
           
            data = []
            
            for row in result:
                data.append({'id':str(row['_id']),'name':row['name']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200        


@apiV1.resource('/skills/<lang_id>')
class Skills(Resource):
    
    def __init__(self):
        self.create_fields = {'title': {'type': 'string','empty': False,'required':True},
                              'url': {'type': 'string','empty': False,'required':True},
                              'type': {'type':'string','required':True,'allowed': ['video','document','image','url']}}
  
    def get(self,lang_id):
        try:
            result = mongo.db.skills.find({'lang_id':getId(lang_id)})
            data = []
            
            user_id = getId(getCurrentUserId())
            
            docs = self.getDocIds(user_id)
            
            for row in result:
                if row['type'] == 'document':
                    row['url'] = app.config['DOC_URL']+ "skills/download/"+row['url']
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
                json['lang_id'] = getId(lang_id)
                json['title'] = temp['title']
                json['url'] = temp['url']
                json['type'] = temp['type']
                json['status'] = 1
                json['created_at'] = datetime.now()
                
                id = mongo.db.skills.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["Language exist."]}},400
        
    
  


@apiV1.resource('/skills/read/<id>')
class SkillsRead(Resource):
    
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
        
  
