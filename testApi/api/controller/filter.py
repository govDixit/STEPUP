from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getRow,getId,getCurrentUserId, dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
from api.controller import city



@apiV1.resource('/filter')
class Filter(Resource):
    
    def __init__(self):
        self.create_fields = {'title': {'type': 'string','empty': False,'required':True},
                              'url': {'type': 'string','empty': False,'required':True},
                              'type': {'type':'string','required':True,'allowed': ['video','document','image','url']}}
  
    def get(self):
        try:
            result = mongo.db.city.find({'status':1})
            city = []
            for row in result:
                city.append({'id':str(row['_id']),'value':row['name']})
            
            data = {}    
            data['filter1'] = {'title':'City','values':city}
            data['filter2'] = {'title':'Gender','values':[{'id':'Male','value':'Male'},{'id':'Female','value':'Female'}]}
            data['filter3'] = {'title':'Type','values':[{'id':'RETAIL','value':'RETAIL'},{'id':'MTO','value':'MTO'},{'id':'LAMP','value':'LAMP'}]}
            
            
            return data,200 
        
        except:
            return {'error':{"message":"Something Wrong."}},400
        
        
        
@apiV1.resource('/brand/select')
class BrandSelect(Resource):
  
    def get(self):
        try:
            result = mongo.db.products.find()
            temp = []
            #print(result)
            for row in result:
                temp.append({'id':str(row['_id']),'name':row['name']})
                
            return temp,200
        
        except:
            return [],400   
        
        
        
@apiV1.resource('/offerBrand/select')
class OfferBrandSelect(Resource):
  
    def get(self):
        try:
            result = mongo.db.offer_products.find()
            temp = []
            #print(result)
            for row in result:
                temp.append({'id':str(row['_id']),'name':row['name']})
                
            return temp,200
        
        except:
            return [],400   
        
        
        
                