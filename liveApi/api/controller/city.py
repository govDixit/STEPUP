from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json




@apiV1.resource('/city/<id>')
class City(Resource):
    
    def __init__(self):
        self.update_fields = {'areas': {'type': 'string','required': True,'empty': True},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self,id):
        result = mongo.db.city.find_one_or_404({"_id":getId(id)})
        
        if result:
            result['areas'] = '\n'.join([str(elem) for elem in result['areas']]) 
            
        return getData(result),200
    
    def put(self,id):
        v = Validator(self.update_fields,allow_unknown=False)
        json = request.get_json()
        if v.validate(json):
            mongo.db.city.find_one_or_404({"_id":getId(id)})
            
            area = json['areas']
            tempArea = area.rsplit('\n')
            
            areas = []
            for row in tempArea:
                row = row.strip()
                if row != '':
                    areas.append(row.upper())
            
            json['areas'] = areas
            
            myquery = {"_id":getId(id)}
            newvalues = {"$set": json}
            
            mongo.db.city.update_one(myquery, newvalues)
            
            result = mongo.db.city.find_one_or_404({"_id":getId(id)})
            return getData(result),200
        else:
            return {'error':v.errors},400
        
    def delete(self,id):
        
        mongo.db.city.find_one_or_404({"_id":getId(id)})
        
        myquery = {"_id":getId(id)}
        newvalues = {"$set": {"status":3}}
        
        mongo.db.city.update_one(myquery, newvalues)
        
        return {'status':'ok'},202
           
           
           
@apiV1.resource('/city')
class CityList(Resource):
    
    def __init__(self):
        self.create_fields = {'name': {'type': 'string','required': True,'empty': False},
                              'areas': {'type': 'string','required': True,'empty': True},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            
            self.user = getCurrentUser() 
            # City Manager Filter
            if self.user['role'] == 3:
                data = {"draw":0,"recordsTotal":0,"recordsFiltered":0,"data":[]}
                return data,200
            
            if search != '':
                result = mongo.db.city.find({'name':{'$regex' : search, '$options' : 'i'}}).skip(start).limit(length).sort([('status', -1)])
            else:
                result = mongo.db.city.find().skip(start).limit(length).sort([('status', -1)])
                
            total = result.count()
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = getData(result)
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            #return json,200
            if v.validate(json):
                
                area = json['areas']
                tempArea = area.rsplit('\n')
                
                areas = []
                for row in tempArea:
                    row = row.strip()
                    if row != '':
                        areas.append(row.upper())
                
                json['areas'] = areas
                
                
                json['status'] = int(json['status'])
                id = mongo.db.city.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["City already exist."]}},400
           
  



@apiV1.resource('/city/select')
class CitySelect(Resource): 
    def get(self):
        try:    
            query = {}
            #for City Manager Login
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                query['_id'] = getId(self.user['city_id'])     
                  
            result = mongo.db.city.find(query)
           
            data = []
            
            for row in result:
                data.append({'id':str(row['_id']),'name':row['name'],'areas':row['areas']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200




@apiV1.resource('/city/area/<id>')
class CityAreaSelect(Resource): 
    def get(self,id):
        try:           
            result = mongo.db.city.find_one({"_id":getId(id)})
            
            data = []
            if result:
                data = result['areas']
            
           
                
            return data,200
        except Exception as e:
            print(e)
            return [],200
        
        
