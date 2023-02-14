from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json


@apiV1.resource('/city/test')
class CityTest(Resource):
    def get(self):
        length = int(request.args.get('length',10))
        start = int(request.args.get('start',0))
        search = request.args.get('search')
        city_id = request.args.get('city_id',0)
        
        query = {}
        if city_id != 0:
            query['city_id'] = getId(city_id)
        if search != '':
            query['$or'] = [{'name':{'$regex' : search, '$options' : 'i'}}]
            
       
        result = mongo.db.city.find(query).skip(start).limit(length)
            
        total = result.count()
        
        data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
        data['data'] = getData(result)
        return data,200

@apiV1.resource('/city/<id>')
class City(Resource):
    
    def __init__(self):
        self.update_fields = {'status': {'allowed': [0, 1]}}
        
    def get(self,id):
        result = mongo.db.city.find_one_or_404({"_id":getId(id)})
        return getData(result),200
    
    def put(self,id):
        v = Validator(self.update_fields,allow_unknown=False)
        json = request.get_json()
        if v.validate(json):
            mongo.db.city.find_one_or_404({"_id":getId(id)})
            
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
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            if search != '':
                result = mongo.db.city.find({'name':{'$regex' : search, '$options' : 'i'}}).skip(start).limit(length)
            else:
                result = mongo.db.city.find().skip(start).limit(length)
                
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
            result = mongo.db.city.find()
           
            data = []
            
            for row in result:
                data.append({'id':str(row['_id']),'name':row['name']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200
