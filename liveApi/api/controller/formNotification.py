from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow,getCurrentUserId,getCurrentUser,dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from bson import ObjectId
from api.lib.outletLib import OutletLib

import os
import base64


@apiV1.resource('/form/notification')
class FormNotification(Resource):
    
    def __init__(self):
        self.create_fields = {}
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            city_id = request.args.get('city_id','0')
           
            query = {}
            if city_id != '0':
                query['city_id'] = getId(city_id)
            if search != '':
                query['$or'] = [{'name':{'$regex' : search, '$options' : 'i'}},{'code':search}]
                
            #for City Manager Login
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])      
                
            result = mongo.db.notification.find(query).skip(start).limit(length).sort([('_id', -1)])
            #result = mongo.db.notification.find({}).sort([('_id', -1)])
            total = result.count()
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = getData(result)
            return data,200
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
        
    def post(self):
        try:
            json = request.get_json()
            #print(json)
            data = {}
            data['user_id'] = getId(getCurrentUserId())
            
            
            for f in json:
                data[f['name']] = f['value']
                
            del data['signature']
            
            data['city_id'] = getId(data['city_id'])
            data['outlet_id'] = getId(data['outlet_id'])
            data['activity_id'] = getId(data['activity_id'])
            coardinates = data['coardinates'].split(",")
            data['coardinates'] = {'latitude':coardinates[0],'longitude':coardinates[1]}
            
            dateInput = dateTimeValidate(data['date'])
            #print(dateInput.date())
            data['date'] = dateInput
            
            id = mongo.db.notification.insert(data)
            
            today_date = datetime.strptime(str(dateInput.date()),"%Y-%m-%d")
            
            myquery = {"user_id":data['user_id'],"date":today_date}
            newvalues = { "$inc": {"error_level": int(1)} }
            #print(myquery)
            
            mongo.db.attendance.update_one(myquery, newvalues)
            
            return {'status':'ok','id':str(id)},201
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400  
           
 
 
@apiV1.resource('/form/notification/<form_id>')
class FormNotificationById(Resource):
    
    def __init__(self):
        self.create_fields = {}
    
    
    def get(self,form_id):
        
        result = mongo.db.form_fields.find()
        f = {}
        for row in result:
            f[str(row['_id'])] = row['label']
        
       
        row = mongo.db.notification.find_one({'_id':getId(form_id)})
        
        data = []
        if row:
            del row['_id']
            for k in row.keys(): 
                if k == 'user_id':
                    data.append({'id':'User','value':self.getUser(row[k])})
                elif k == 'city_id':
                    data.append({'id':'City','value':self.getCity(row[k])})
                elif k == "outlet_id":
                    data.append({'id':'Outlet','value':self.getOutlet(row[k])})
                elif k == "date":
                    data.append({'id':'Date','value':str(row[k])})
                elif k == "age":
                    data.append({'id':'Age','value':str(row[k])})
                elif k == "smoker":
                    data.append({'id':'Smoker','value':str(row[k])})
                elif k == "participate":
                    data.append({'id':'Participate','value':str(row[k])})
                elif k == "name":
                    data.append({'id':'Name','value':str(row[k])})
                elif k == "brands":
                    data.append({'id':'Brands','value':str(row[k])})
                elif k == "variant":
                    data.append({'id':'Variant','value':self.getVariant(str(row['brands']),str(row[k]))})
                elif k == "signature":
                    t = {}
                    #data.append({'id':'Signature','value':str(row[k])})
                elif k == "status":
                    data.append({'id':'Status','value':str(row[k])})
                elif k == "comments":
                    data.append({'id':'Comments','value':str(row[k])})
                elif k == "activity_id":
                        t = {}
                elif k == "coardinates":
                    data.append({'id':'Latitude','value':row[k]['latitude']})
                    data.append({'id':'Longitude','value':row[k]['longitude']})
                else:
                    data.append({'id':f[str(k)],'value':str(row[k])})
        #self.base64ToImage(form_id, result['signature'])
        return data,200
    
    def base64ToImage(self, form_id, imgstring):
        imgdata = base64.b64decode(imgstring)
        
        filename = os.path.join(app.config['UPLOAD_FOLDER']+"signature/", form_id+".jpg")
        with open(filename, 'wb') as f:
            f.write(imgdata)
            
    def getUser(self,id):
        row = mongo.db.users.find_one({'_id':id})
        if row:
            return row['name'];
        return 'None'
    
    def getOutlet(self,id):
        row = mongo.db.outlet.find_one({'_id':getId(id)})
        if row:
            return row['name'];
        return 'None'
    
    def getCity(self,id):
        row = mongo.db.city.find_one({'_id':getId(id)})
        if row:
            return row['name'];
        return 'None'
    
    def getVariant(self,brand_id,variant_id):
        row = mongo.db.products.find_one({'id':getId(brand_id)})
        if row:
            for v in row['variant']:
                if variant_id == str(v['id']):
                    return v['name']
        return 'None'
  
  
  
  
  