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

import os
import base64

  
@apiV1.resource('/form/field')
class FormField(Resource):
    def __init__(self):
        self.create_fields = {'name': {'type': 'string','required':True,'empty': False},
                              'label': {'type': 'string','required':True,'empty': False},
                              'tag': {'type': 'string','required':True,'empty': False},
                              'type': {'type': 'string','required':True,'empty': False},
                              'options': {'type': 'string','required':False},
                              'priority': {'type': 'number','required':True,'empty': False},
                              'required': {'type': 'number','required':True,'allowed': [0, 1]},
                              'status': {'type':'number','required':True,'allowed': [0, 1]},
                              'city_ids': {'type':'string','required':True,'empty': True}}
           
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            city_id = request.args.get('city_id','0')
            
            query = {}
            if city_id != '0':
                query['_id'] = {'$in':self.__fieldIds(city_id)}
            if search != '':
                query['$or'] = [{'label':{'$regex' : search, '$options' : 'i'}},{'name':search}]
                
            #print(query)
            result = mongo.db.form_fields.find(query).skip(start).limit(length)
                
            total = result.count()
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = getData(result)
            return data,200
        except Exception as e:
            print(e)
            return [],200
        
    def __fieldIds(self,city_id):
        result = mongo.db.city_form_fields.find({'city_id':getId(city_id)})
        temp = []
        for row in result:
            temp.append(row['form_field_id'])
        return temp
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                data = {}
                
                data['_id'] = ObjectId()
                data['name'] = str(data['_id'])
                data['label'] = json['label']
                data['tag']  = json['type']
                data['type']  = json['type']
                data['priority']  = json['priority']
                data['status']  = json['status']
                city_ids  = json['city_ids']
                data['validation'] = {}
                
                if "name" in json: 
                    data['name'] = json['name']
                     
                if data['type'] == "checkbox" or data['type'] == "radio" or data['type'] == "rating":
                    data['options']  = json['options'].split(',')
                    data['validation']["allowed"] =  data['options']
                else:
                    data['options']  = None
                    
                if json['required'] == 1:
                    data['validation']['required'] = True
                else:
                    data['validation']['required'] = False
                    
                
                
                data['step']  = 2
                
                result = mongo.db.form_fields.insert(data)
                return {'status':'ok','id':str(result)},201
            else:
                return {'error':v.errors},400
        
        except DuplicateKeyError:
            return {'error':{"message":"Form Field already exist."}},400
    
 
 
@apiV1.resource('/form/field/<id>')
class FormFieldById(Resource):
    
    def __init__(self):
        self.update_fields = {
                              #'name': {'type': 'string','required':True,'empty': False},
                              'label': {'type': 'string','required':True,'empty': False},
                              'tag': {'type': 'string','required':True},
                              'type': {'type': 'string','required':True,'empty': False},
                              'options': {'type': 'string'},
                              'priority': {'type': 'number','required':True,'empty': False},
                              'required': {'type': 'number','required':True,'allowed': [0, 1]},
                              'status': {'type':'number','required':True,'allowed': [0, 1]},
                              'city_ids': {'type':'string','required':True,'empty': True}}
        
    def get(self,id):
        try:
            result = mongo.db.form_fields.find_one_or_404({"_id":getId(id)})
            
            cities = mongo.db.city_form_fields.find({"form_field_id":getId(id)})
            city_ids = []
            
            for city in cities:
                city_ids.append(str(city['city_id']))
                
           
            result['city_ids'] = city_ids;  
            return getData(result),200
        except Exception as e:
            print(e)
            return [],200
        
    def put(self,id):
        try:
            v = Validator(self.update_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                data = {}
                
                data['_id'] = ObjectId()
                data['name'] = str(data['_id'])
                data['label'] = json['label']
                data['tag']  = json['type']
                data['type']  = json['type']
                data['priority']  = json['priority']
                data['status']  = json['status']
                city_ids  = json['city_ids']
                data['validation'] = {}
                
                if "name" in json: 
                    data['name'] = json['name']
                     
                if data['type'] == "checkbox" or data['type'] == "radio" or data['type'] == "rating":
                    data['options']  = json['options'].split(',')
                    data['validation']["allowed"] =  data['options']
                else:
                    data['options']  = None
                    
                if json['required'] == 1:
                    data['validation']['required'] = True
                else:
                    data['validation']['required'] = False
                
                data['step']  = 2
                
                myquery = {"_id":getId(id),"step":2}
                newvalues = {"$set": json}
            
                mongo.db.form_fields.update_one(myquery, newvalues)
                self.__AddtoCity(id,city_ids)
                result = mongo.db.form_fields.find_one_or_404({"_id":getId(id)})
                
                return {'status':'ok','id':str(result)},200
            else:
                return {'error':v.errors},400
        
        except DuplicateKeyError:
            return {'error':{"message":"Form Field already exist."}},400
        
        
    def __AddtoCity(self,form_field_id,city_ids):
        #if city_ids != 
        city_ids = city_ids.split(",");
        c = 0
        #print(len(city_ids));
        if len(city_ids) > 0:
            mongo.db.city_form_fields.remove({"form_field_id":getId(form_field_id)})
            
        for city_id in city_ids:
            try:
                if(getId(city_id)):
                    mongo.db.city_form_fields.insert({'city_id':getId(city_id),"form_field_id":getId(form_field_id),"priority":0})
            except:
                c = c+1
        return True
            
           
 
@apiV1.resource('/form/field/city')
class FormCity(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'type': 'string','required': True,'empty': False},
                              'form_field_id': {'type': 'string','required': True,'empty': False}}
           
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                json['city_id'] = getId(json['city_id'])
                json['form_field_id'] = getId(json['form_field_id'])
                id = mongo.db.city_form_fields.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":"Form Field already exist."}},400
        


@apiV1.resource('/form/field/city/<city_id>')
class FormCityById(Resource):
    
    def get(self,city_id):
        try:
            brands = self.__getBrands()
            
            #self.__updateProductFormFields()
            step1 = []
            result = mongo.db.form_fields.find({"status":1,"step":1})
            if result:   
                for row in result:
                    if row['type'] == "select":
                        row['options2'] = []
                        for t in row['options']:
                            row['options2'].append({'id':t,'name':t})
                       
                        row['options'] = None
                    step1.append(getData(row))       
            
            aggr = [{"$lookup": { "from": "city_form_fields", "localField": "_id", "foreignField": "form_field_id", "as": "city"}},{ "$unwind": "$city"}]
            aggr.append({"$match":{"status":1,"city.city_id":getId(city_id)}})
            aggr.append({"$sort":{"city.priority":1}})
                
            result = mongo.db.form_fields.aggregate(aggr)
            
            
            step2 = []
            
            if result:   
                for row in result:
                    del row['city']
                    if row['name'] == "brands":
                        row['options'] = None
                        row['options2'] = brands
                    elif row['type'] == "select":
                        row['options2'] = row['options']
                        row['options'] = None
                        
                        
                    step2.append(getData(row))
                        
                return {'step1':step1,'step2':step2},200
            else:
                return {'error':{"message":"City Id is not found"}},404
       
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400
    
    
    
    
    def __getBrands(self):
        result = mongo.db.products.find()
        temp = []
        for row in result:
            del row['status']
            t = []
            for v in row['variant']:
                del v['status']
                v['id'] = v['name'];
                t.append(getRow(v))
                
            row['variant'] = t
            #print(row)
            temp.append(getRow(row))
            
        return temp
    
    
    def __insertCityFormFields(self,city_id):
        try:
            result = mongo.db.form_fields.find({"step":2})
            for row in result:
                mongo.db.city_form_fields.insert({'city_id':getId(city_id),"form_field_id":row['_id'],"priority":0})
            return True
        except:
            return False
        
    def __updateProductFormFields(self):
        try:
            
            result = mongo.db.products.find({"status":1})
            products = {}
            products_ids = []
            for row in result:
                products[str(row['_id'])] = row['name'];
                products_ids.append(str(row['_id']))
                
            mongo.db.form_fields.update_one({"name":"brands"}, {"$set":{"options":products,"validation.allowed":products_ids}})
            
            return True
        except:
            return False
            
            



@apiV1.resource('/form/field/city/sample/<city_id>')
class FormCityByIdSample(Resource):
    
    def get(self,city_id):
        try:
            brands = self.__getBrands()
            
            #self.__updateProductFormFields()
            temp = []
            result = mongo.db.form_fields.find({"status":1,"step":1})
            if result:   
                for row in result:
                    if row['options'] == None:
                        temp.append({'name':row['name'],'value':row['name']})
                    else:
                        temp.append({'name':row['name'],'value':row['options'][0]})
            
            aggr = [{"$lookup": { "from": "city_form_fields", "localField": "_id", "foreignField": "form_field_id", "as": "city"}},{ "$unwind": "$city"}]
            aggr.append({"$match":{"status":1,"city.city_id":getId(city_id)}})
            aggr.append({"$sort":{"city.priority":1}})
                
            result = mongo.db.form_fields.aggregate(aggr)
            
            if result:   
                for row in result:
                    if row['options'] == None:
                        temp.append({'name':row['name'],'value':row['name']})
                    else:
                        temp.append({'name':row['name'],'value':'5d981a525581b73e99d6b584'})
                        
                    if row['name'] == "brands":
                        temp.append({'name':'variant','value':'Red'})
                        
                return temp,200
            else:
                return {'error':{"message":"City Id is not found"}},404
       
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400
    
    
    
    
    def __getBrands(self):
        result = mongo.db.products.find()
        temp = []
        for row in result:
            del row['status']
            t = []
            for v in row['variant']:
                del v['status']
                t.append(getRow(v))
                
            row['variant'] = t
            #print(row)
            temp.append(getRow(row))
            
        return temp