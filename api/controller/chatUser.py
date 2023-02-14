from api import app, mongo, apiV1
from flask import request,send_file
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from api.lib.helper import getData,getId,getRow
                
@apiV1.resource('/chat/user')
class ChatUserList(Resource):
       
    def get(self):
        try:
            users = mongo.db.users.find()
            temp = []
            for row in users:
                t = {}
                t['id'] = str(row['_id'])
                t['name'] = row['name']
                t['code'] = row['code']
                t['role'] = row['role']
                t['profile_pic'] =  app.config['BASE_URL']+row['profile_pic']
                temp.append(t)
                
            return temp,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
        
@apiV1.resource('/chat/user/<id>')
class ChatUserListById(Resource):
       
    def get(self,id):
        try:
            r = range(1, 5)
            users = []
            
            if getId(id):
                users = mongo.db.users.find({'parent_id':getId(id)})
            elif int(id) in r:
                users = mongo.db.users.find({'role':int(id)})
            
            temp = []
            for row in users:
                t = {}
                t['id'] = str(row['_id'])
                t['name'] = row['name']
                t['code'] = row['code']
                t['role'] = row['role']
                t['profile_pic'] =  app.config['BASE_URL']+row['profile_pic']
                temp.append(t)
                
            return temp,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
        
