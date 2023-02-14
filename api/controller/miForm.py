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


@apiV1.resource('/form')
class MiFormList(Resource):
    
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
                
            
            result = mongo.db.miform.find(query).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = getData(result)
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
    
    def post(self):
        try:
            result = mongo.db.form_fields.find({'status':1},{'name': 1, 'validation': 1})
            fields = {}
            
            """for row in result:
                if row['validation']:
                    fields[row['name']] = row['validation']
            
            fields['date'] = {'type': 'date','empty': False,'required':True}
            self.create_fields = fields
            
            
            v = Validator(self.create_fields,allow_unknown=False)"""
            json = request.get_json()
            data = {}
            data['user_id'] = getId(getCurrentUserId())
            
            for f in json:
                try:
                    data[f['name']] = f['value']
                except:
                    t = {}
            
            data['city_id'] = getId(data['city_id'])
            data['outlet_id'] = getId(data['outlet_id'])
            
            if 'activity_id' in data:
                data['activity_id'] = getId(data['activity_id'])
            else:
                data['activity_id'] = None; #getId(data['activity_id'])
                
            data['brands'] = getId(data['brands'])
            coardinates = data['coardinates'].split(",")
            data['coardinates'] = {'latitude':coardinates[0],'longitude':coardinates[1]}
            
            dateInput = dateTimeValidate(data['date'])
            data['date'] = dateInput
            
            if True:
                id = ObjectId()
                signature = data['signature']
                filename = os.path.join(app.config['UPLOAD_FOLDER']+"signature/", str(id)+".jpg")
                
                data['_id'] = id
                data['status'] = 0
                data['comments'] = None
                data['signature'] = filename
                mongo.db.miform.insert(data)
                self.__debitStock(data['user_id'],data['brands'],data['variant'])
                self.base64ToImage(signature, filename)
                
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':"Errors",'validataion':fields},400
        except DuplicateKeyError:
            return {'error':{"message":"Form already exist."}},400
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
        
    def __debitStock(self,user_id,brand_id,variant_id):
        
        if str(brand_id) != '5d981ae25581b73e99d6b5c7':
            return False
        
        result = mongo.db.products.find_one({'_id':getId('5d981ae25581b73e99d6b5c7')})
        stock_id = 0;
        for row in result['variant']:
            if row['name'] == variant_id:
                stock_id = str(row['id'])
        
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        myquery = {"user_id":getId(user_id),"date":self.dateInput}
        newvalues = { "$inc": {"stock."+stock_id+".debit": int(1)} }
        #print(newvalues)
        mongo.db.stocks.update_one(myquery, newvalues)


    def base64ToImage(self, signature, filename):
        imgdata = base64.b64decode(signature)
        with open(filename, 'wb') as f:
            f.write(imgdata)
        

@apiV1.resource('/form/<form_id>')
class MiForm(Resource):
    
    def __init__(self):
        self.create_fields = {}
    
    
    def get(self,form_id):
        try:
            result = mongo.db.form_fields.find()
            f = {}
            for row in result:
                #print(row)
                f[str(row['name'])] = row['label']
            
            #print(f)
            
            row = mongo.db.miform.find_one({'_id':getId(form_id)})
            
            
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
                        t = self.getVariant(row['brands'],str(row['variant']))
                        data.append({'id':'Brands','value':t['brand']})
                        data.append({'id':'Variant','value':t['variant']})
                    elif k == "variant":
                        t = {}
                    #   data.append({'id':'Variant','value':self.getVariant(str(row['brands']),str(row[k]))})
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
        except Exception as e:
            print(e)
            return [],200
    
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
        row = mongo.db.products.find_one({'_id':getId(brand_id)})
       
        if row:
            for v in row['variant']:
                if variant_id == str(v['name']):
                    return {'brand':row['name'],'variant':v['name']}
            return {'brand':row['name'],'variant':''}
        return {'brand':'','variant':''}
    
    
