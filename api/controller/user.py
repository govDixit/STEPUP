from api import app, mongo, apiV1
from flask import request,send_file
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from api.lib.helper import getData,getId,getRow
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import hashlib 
import json
import os
import base64
import pandas as pd
from io import StringIO

"""class CustomErrorHandler(errors.BasicErrorHandler):
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.MAX_VALUE.code] = 'Status value is not a Valid!'"""



@apiV1.resource('/user/<id>')
class User(Resource):
    
    def __init__(self):
        self.update_fields = {'name': {'type': 'string','empty': False},
                              'code': {'type': 'string','empty': False},
                              'email': {'type': 'string','empty': False},
                              #'mobile': {'type': 'number','empty': False,'minlength':10,'maxlength':10},
                              'password': {'type': 'string','minlength':6,'maxlength':16},
                              'confirmPassword': {'type': 'string','minlength':6,'maxlength':16},
                              'status': {'type':'number','allowed': [0, 1]},
                              #'parent_id': {'required': True},
                              'role': {'type':'number','allowed': [1, 2,3,4]}}
        
    def get(self,id):
        try:
            user = mongo.db.users.find_one({"_id":getId(id)})
            if user:
                user.pop('password')
                #if user['parent_id']
                return getData(user),200
            else:
                return {'error':{"message":"User is not found."}},404
        except:
            return {'error':{"message":"Something Wrong"}},400
    
    def put(self,id):
        v = Validator(self.update_fields,allow_unknown=False)
        json = request.get_json()
        if v.validate(json):
            if 'password' in json: 
                if json['password'] != json['confirmPassword']:
                    return {'error': {"confirmPassword": ["Password and Confirm Password are not matching."]}}, 400
                del json['confirmPassword']
                json['password'] =  hashlib.md5(json['password'].encode()).hexdigest()
                
                
            
            """json['profile_pic'] = 'user.png'
            json['parent_id'] = getId(json['parent_id'])
            
            #if not json['parent_id']:
            if json['role'] == 1 and json['parent_id'] == False:
                return {'error':{"supervisor":"Supervisor is missing or not valid.","city_manager":"City Manager is missing or not valid."}},400
            elif json['role'] == 2 and json['parent_id'] == False:
                return {'error':{"city_manager":"City Manager is missing or not valid."}},400
            if json['parent_id'] == False:
                json['parent_id'] = None"""
                    
                    
            user = mongo.db.users.find_one_or_404({"_id":getId(id)})
            
            myquery = {"_id":getId(id)}
            newvalues = {"$set": json}
            
            mongo.db.users.update_one(myquery, newvalues)
            
            user = mongo.db.users.find_one_or_404({"_id":getId(id)})
            return getData(user),200
        else:
            return {'error':v.errors},400
        
    def delete(self,id):
        
        user = mongo.db.users.find_one_or_404({"_id":getId(id)})
        
        myquery = {"_id":getId(id)}
        newvalues = {"$set": {"status":3}}
        
        mongo.db.users.update_one(myquery, newvalues)
        
        return {'status':'ok'},202
           
           
           
@apiV1.resource('/user')
class UserList(Resource):
    
    def __init__(self):
        self.create_fields = {'name': {'type': 'string','required': True,'empty': False},
                              'code': {'type': 'string','required': True,'empty': False},
                              'email': {'type': 'string','required': True,'empty': False},
                              'mobile': {'type': 'number','required': True,'empty': False,'minlength':10,'maxlength':10},
                              'password': {'type': 'string','required': True,'empty': False,'minlength':6,'maxlength':16},
                              'confirmPassword': {'type': 'string','required': True,'empty': False,'minlength':6,'maxlength':16},
                              'status': {'type':'number','required': True,'allowed': [0, 1]},
                              'parent_id': {'required': True},
                              'role': {'type':'number','required': True,'allowed': [1, 2,3,4]}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            role = int(request.args.get('role',4))
            parent_id = request.args.get('parent_id',0)
            
            query = {}
            if parent_id != 0:
                query['parent_id'] = getId(parent_id)
            if search != '':
                query['$or'] = [{'name':{'$regex' : search, '$options' : 'i'}},{'code':search}]
                
            query['role'] = role  
            
            user_results = mongo.db.users.find(query).skip(start).limit(length)
                
            total = user_results.count()
            
            users = []
            parent_ids = []
            parent_users = {}
            for row in user_results:
                if row['parent_id'] != None:
                    parent_ids.append(row['parent_id'])
                users.append(getRow(row))
            
            
            #Fetch parent names   
            if len(parent_ids) > 0: 
                result = mongo.db.users.find({"_id": {"$in": parent_ids}})
                for row in result:
                    parent_users[str(row['_id'])] = row['name']
            
           
            for row in users:
                try:
                    if row['parent_id'] != None:
                        row['parent_name'] = parent_users[str(row['parent_id'])]
                    else:
                        row['parent_name'] = 'None'
                except:
                    row['parent_name'] = 'None'   
                
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = users
            return data,200
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
           
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                if json['password'] != json['confirmPassword']:
                    return {'error': {"confirmPassword": ["Password and Confirm Password are not matching."]}}, 400
                
                del json['confirmPassword']
                json['profile_pic'] = 'user.png'
                json['parent_id'] = getId(json['parent_id'])
                
                #if not json['parent_id']:
                if json['role'] == 1 and json['parent_id'] == False:
                    return {'error':{"supervisor":"Supervisor is missing or not valid.","city_manager":"City Manager is missing or not valid."}},400
                elif json['role'] == 2 and json['parent_id'] == False:
                    return {'error':{"city_manager":"City Manager is missing or not valid."}},400
                if json['parent_id'] == False:
                    json['parent_id'] = None
                    
                #print(json);
                json['password'] =  hashlib.md5(json['password'].encode()).hexdigest()
                id = mongo.db.users.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error': v.errors}, 400
        except DuplicateKeyError:
            return {'error':{"message":"User already exist."}},400
 


    
@apiV1.resource('/user/select')
class UserSelect(Resource): 
    def get(self):
        try:           
            users = mongo.db.users.find({'role':3})
            user_ids = []
            users_dict = {}
            data = {}
                    
            for row in users:
                data[str(row['_id'])] = {'id':str(row['_id']),'name':row['name'],'supervisor':[]}
                user_ids.append(getId(row['_id']))   
                
            result = mongo.db.users.find({"parent_id": {"$in": user_ids}}) 
            for row in result:
                data[str(row['parent_id'])]['supervisor'].append({'id':str(row['_id']),'name':row['name']})
            
            
            """aggr = [{"$lookup": { "from": "users", "localField": "parent_id", "foreignField": "_id", "as": "parent"}},{ "$unwind": "$parent"}]
            aggr.append({"$match":{"role":2}})
            
            
            aggr = [{"$lookup": { "from": "users", "localField": "_id", "foreignField": "parent_id", "as": "supervisor"}},{ "$unwind": "$supervisor","preserveNullAndEmptyArrays": "true"}]
            aggr.append({"$match":{"role":3}})
            
            users = mongo.db.users.aggregate(aggr)
            data = {}
            temp = []
            
            for row in users:
                supervisor = row['supervisor']
                
                if str(row['_id']) in data:
                    data[str(row['_id'])]['supervisor'].append({'id':str(supervisor['_id']),'name':supervisor['name']})
                else:
                    data[str(row['_id'])] = {'id':str(row['_id']),'name':row['name'],'supervisor':[]}
                    data[str(row['_id'])]['supervisor'].append({'id':str(supervisor['_id']),'name':supervisor['name']})"""
              
            temp = []
            for key in data:
                temp.append(data[key])
                
            return temp,200
        except Exception as e:
            print(e)
            return [],200
        
@apiV1.resource('/user/select/<id>')
class UserSelectByParent(Resource): 
    def get(self,id):
        try:           
            users = mongo.db.users.find({'parent_id':getId(id)})
           
            data = []
            
            for row in users:
                data.append({'id':str(row['_id']),'name':row['name']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200
 
           
@apiV1.resource('/user/child/<parent_id>')
class UserListByParent(Resource):
   
    def get(self,parent_id):
        try:
            user = mongo.db.users.find({'parent_id':getId(parent_id)})
            return getData(user),200
        except:
            return {'error':{"message":"Something Wrong"}},400
    
   
    
@apiV1.resource('/profile')
class UserProfile(Resource):
    def get(self):
        profile_id = get_jwt_identity()
        user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})
        user.pop('password') 
        return {'profile': getData(user)},200
    
    def put(self):
        return {'hello': 'world put method'}
    
    
    
    



@apiV1.resource('/user/import')
class UserImport(Resource):
    
    def post(self):
        try:
            json = request.get_json()
            users = json['user']
            users = users.split(',')[1]
            role = json['role']
            #users = users.replace("data:text/csv;base64", "")
            
            parent_id = getId(json['parent_id'])
            
            #if not json['parent_id']:
            if json['role'] == 1 and parent_id == False:
                return {'error':{"supervisor":"Supervisor is missing or not valid.","city_manager":"City Manager is missing or not valid."}},400
            elif json['role'] == 2 and parent_id == False:
                return {'error':{"city_manager":"City Manager is missing or not valid."}},400
            if parent_id == False:
                parent_id = None;
                
            
            #print(outlets)
            
            code_string = base64.b64decode(users)
            #code_string = code_string.decode('utf-8')
            code_string = code_string.decode('utf-8',errors="ignore")
            TESTDATA = StringIO(code_string)
            df = pd.read_csv(TESTDATA, sep=",")
            
            #print(df)
         
            #return {'status':'ok'},201
            for index, row in df.iterrows():
                password = str(row['password'])
                t = {}
                t['name'] = row['name']
                t['code'] = row['code']
                t['email'] = row['email']
                t['mobile'] = row['mobile']
                t['password'] = hashlib.md5(password.encode()).hexdigest()
                t['status'] = 1
                t['role'] = role
                t['parent_id'] = parent_id
                t['profile_pic'] = "user.png"
                mongo.db.users.insert(t)
             
            return {'status':'ok'},201
        
        except DuplicateKeyError:
            return {'error':{"message":["User already exist."]}},400
        except Exception as e:
            print(e)
            return {'error':{"message":["Something wrong."]}},400
            
    
    