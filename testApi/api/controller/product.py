from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from bson import ObjectId


@apiV1.resource('/products')
class PropuctList(Resource):
    
    def get(self):
        try:
            result = mongo.db.offer_products.find()
            return getData(result),200
            
            """result = mongo.db.products.find_one({'_id':getId('5d981ae25581b73e99d6b5c7')})
            temp = []
            #print(result)
            for row in result['variant']:
                temp.append(getRow(row))
                
            return temp,200"""
        except:
            return {'error':{"message":"Something Wrong."}},400    
    

@apiV1.resource('/products/variant/<id>')
class PropuctVariant(Resource):
    
 
    def post(self,id):
        try:
            json = request.get_json()
           
            myquery = {'_id':getId(id)}
            newvalues = {"$addToSet": {"variant":{'id':ObjectId(),'name':json['name'],'status':1}}}
            #mongo.db.products.update_one(myquery,newvalues)  
            
                
            return {'status':'ok'},200 
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400    