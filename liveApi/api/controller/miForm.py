from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow,getCurrentUserId,getCurrentUser,dateTimeValidate,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from bson import ObjectId
from api.lib.outletLib import OutletLib

import os
import base64
import pandas as pd
#import modin.pandas as pd
import time


@apiV1.resource('/form')
class MiFormList(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {}
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            fwp_code = request.args.get('fwp_code','')
            outlet_code = request.args.get('outlet_code','')
            city_id = request.args.get('city_id','0')
            fromDate = request.args.get('fromDate','0')
            toDate = request.args.get('toDate','0')
            
            query = {}
            if city_id != '0':
                query['city_id'] = getId(city_id)
                
            if fwp_code != '':
                fwp_id  = self.getUserId(fwp_code)
                if fwp_id:
                    query['user_id'] = fwp_id
                    
            if outlet_code != '':
                outlet_id  = self.getOutletId(outlet_code)
                if outlet_id:
                    query['outlet_id'] = outlet_id
            
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            fromDate = fromDate +" 00:00:00"
            toDate = toDate + " 23:59:59"
            
            fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d %H:%M:%S")
            toDate1 = datetime.strptime(str(toDate),"%Y-%m-%d %H:%M:%S") # + timedelta(days=1)
            
            query['date'] = {"$gte": fromDate1, "$lt": toDate1}
            
            #for City Manager Login
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])      
            
            #print(query)
            result = mongo.db.miform.find(query).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = getData(result)
            return data,200
        except Exception as e:
            return {'error':{"message":"Something Wrong "+str(e)}},400
        
    def getUserId(self,code):
        try:
            user = mongo.db.users.find_one({'code':code})
            if user:
                return user['_id']
            else:
                return False
            
        except:
            return False
    
    def getOutletId(self,code):
        try:
            outlet = mongo.db.outlet.find_one({'code':code})
            if outlet:
                return outlet['_id']
            else:
                return False
            
        except:
            return False
    
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
                    if f['name'] == 'brands':
                        data[f['name']] = f['value']
                        data['variant'] = ''
                    elif f['name'] == 'variant':
                        if f['value'] != '':
                            data[f['name']] = f['value']
                    else:
                        data[f['name']] = f['value']
                except:
                    t = {}
            
            data['city_id'] = getId(data['city_id'])
            data['outlet_id'] = getId(data['outlet_id'])
            
            outlet = mongo.db.outlet.find_one({"_id":data['outlet_id']})
            data['area'] = "OTHER"
            data['program'] = None
            if outlet:
                data['area']  = outlet['area'].upper()
                data['program'] = outlet['type']
            
            if 'activity_id' in data:
                data['activity_id'] = getId(data['activity_id'])
            else:
                data['activity_id'] = None; #getId(data['activity_id'])
                
            if 'offer_brand' in data:
                data['offer_brand'] = getId(data['offer_brand'])
            else:
                data['offer_brand'] = None; #getId(data['activity_id'])
                
            data['brands'] = getId(data['brands'])
            
            
            if 'coardinates' in data:
                coardinates = data['coardinates'].split(",")
                data['coardinates'] = {'latitude':coardinates[0],'longitude':coardinates[1]}
            else:
                data['coardinates'] = {'latitude':0,'longitude':0}
            
            
            
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
                
                #print(data)
                #for dublicate check
                r = mongo.db.miform.find_one({'date':dateInput,'user_id':data['user_id']})
                if r:
                    return {'status':'ok','id':str(r['_id'])},201
                
                mongo.db.miform.insert(data)
                self.__debitStock(id,data['user_id'],data['offer_brand'],dateInput)
                self.base64ToImage(signature, filename)
                
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':"Errors",'validataion':fields},400
        except DuplicateKeyError:
            return {'error':{"message":"Form already exist."}},400
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
        
    def __debitStock(self,form_id,user_id,brand_id,dateInput):
        try:
            """if str(brand_id) != '5d981ae25581b73e99d6b5c7':
                return False
            
            result = mongo.db.offer_products.find_one({'_id':getId('5d981ae25581b73e99d6b5c7')})
            stock_id = 0;
            for row in result['variant']:
                if row['name'] == variant_id:
                    stock_id = str(row['id'])"""
            #print(dateInput.date())
            
            
            self.dateInput = datetime.strptime(str(dateInput.date()),"%Y-%m-%d")
            myquery = {"user_id":getId(user_id),"date":self.dateInput}
            
            newvalues = { "$inc": {"stock."+str(brand_id)+".debit":int(1)},"$addToSet": {"list":form_id}}
            #update form id in stock list for verification
            
            
            #print(newvalues)
            mongo.db.stocks.update_one(myquery, newvalues)
            return True
        except Exception as e:
            print(e)
            return False


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
                        data.append({'id':'User','value':self.getUser(row[k]),'name':k})
                    elif k == 'city_id':
                        data.append({'id':'City','value':self.getCity(row[k]),'name':k})
                    elif k == "outlet_id":
                        data.append({'id':'Outlet','value':self.getOutlet(row[k]),'name':k})
                    elif k == "date":
                        data.append({'id':'Date','value':str(row[k]),'name':k})
                    elif k == "age":
                        data.append({'id':'Age','value':str(row[k]),'name':k})
                    elif k == "smoker":
                        data.append({'id':'Smoker','value':str(row[k]),'name':k})
                    elif k == "participate":
                        data.append({'id':'Participate','value':str(row[k]),'name':k})
                    elif k == "name":
                        data.append({'id':'Name','value':str(row[k]),'name':k})
                    elif k == "offer_brand":
                        data.append({'id':f[str(k)],'value':self.getOfferBrand(row[k]),'name':k})
                    elif k == "brands":
                        t = self.getVariant(row['brands'],str(row['variant']))
                        data.append({'id':f[str(k)],'value':t['brand'],'idValue':str(row['brands']),'name':k})
                        #data.append({'id':'Variant','value':t['variant'],'idValue':str(row['variant']),'name':'variant'})
                        data.append({'id':'Variant','value':str(row['variant']),'idValue':str(row['variant']),'name':'variant'})
                    elif k == "variant":
                        t = {}
                    #   data.append({'id':'Variant','value':self.getVariant(str(row['brands']),str(row[k]))})
                    elif k == "area":
                        data.append({'id':'Area','value':str(row[k]),'name':k})
                    elif k == "program":
                        data.append({'id':'Program','value':str(row[k]),'name':k})
                    elif k == "signature":
                        t = {}
                        #data.append({'id':'Signature','value':app.config['DOC_URL']+"signature/download/"+row['signature'].replace("uploads/signature/",""),'name':k})
                        
                        #data.append({'id':'Signature','value':str(row[k])})
                    elif k == "status":
                        data.append({'id':'Status','value':str(row[k]),'name':k})
                    elif k == "comments":
                        data.append({'id':'Comments','value':str(row[k]),'name':k})
                    elif k == "activity_id":
                        t = {}
                    elif k == "coardinates":
                        data.append({'id':'Latitude','value':row[k]['latitude'],'name':'coardinates'})
                        data.append({'id':'Longitude','value':row[k]['longitude'],'name':'coardinates'})
                    else:
                        data.append({'id':f[str(k)],'value':str(row[k]),'name':k})
                
                if 'signature' in row:
                    data.append({'id':'Signature','value':app.config['DOC_URL']+"signature/download/"+row['signature'].replace("uploads/signature/",""),'name':'signature'})
                        
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
    
    def getOfferBrand(self,id):
        row = mongo.db.offer_products.find_one({'_id':getId(id)})
        if row:
            return row['name'];
        return 'None'
 


    def put(self,form_id):
        try:
            result = mongo.db.form_fields.find({'status':1},{'name': 1, 'validation': 1})
            fields = {}
            json = request.get_json()
            data = {}
            #print(json);
            if True:
                myquery = {"_id":getId(form_id)}
                newvalues = {"$set": json}
            
                mongo.db.miform.update_one(myquery, newvalues)
                return {'status':'ok'},200
            else:
                return {'error':"Errors",'validataion':fields},400
       
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400



@apiV1.resource('/form/export')
class MiFormExport(Resource):
    
    def post(self):
        aggr = []
        try:
            json = request.get_json()
            fwp_code =  json['fwp_code'];
            outlet_code = json['outlet_code'];
            city_id = str(json['city_id']);
            
            query = {}   
           
            if city_id != '0':
                query['city_id'] = getId(city_id)
                
            if fwp_code != '':
                fwp_id  = self.getUserId(fwp_code)
                if fwp_id:
                    query['user_id'] = fwp_id
                    
            if outlet_code != '':
                outlet_id  = self.getOutletId(outlet_code)
                if outlet_id:
                    query['outlet_id'] = outlet_id
                    
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            fromDate = json['fromDate']+" 00:00:00"
            toDate = json['toDate']+ " 23:59:59"
            
            fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d %H:%M:%S")
            toDate1 = datetime.strptime(str(toDate),"%Y-%m-%d %H:%M:%S") # + timedelta(days=1)
            
            query['date'] = {"$gte": fromDate1, "$lt": toDate1}
            
        
            #for City Manager Login
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])   
            
            
            result = mongo.db.form_fields.find({},{'name': 1,'label':1})
            cols = {}
            for row in result:
                cols[row['name']] = row['label']
            
            
            result = mongo.db.products.find({})
            for row in result:
                #for v in row['variant']:
                #    cols[str(row['id'])] = row['name']
                cols[str(row['_id'])] = row['name']
                
            result = mongo.db.offer_products.find({})
            for row in result:
                cols[str(row['_id'])] = row['name']
                
            result = mongo.db.city.find({})
            for row in result:
                cols[str(row['_id'])] = row['name']
            
            
            aggr = [{"$lookup": { "from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"},{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            
            aggr.append({"$match":query})
             
            #print(aggr)
            result = mongo.db.miform.aggregate(aggr,allowDiskUse=True)
            
            #result = mongo.db.miform.find(query).sort([('_id', -1)])
            data = []
            c = 0
            for row in result:
                c = c+1
                
                try:
                    outlet = row['outlet']
                    fwp = row['user']
                    
                    
                    del row['activity_id']
                    del row['user_id']
                    del row['user']
                    del row['outlet']
                    #del row['signature']
                    
                    row = getRow(row)
                    del row['id']
                    del row['outlet_id']
                    
                    row['OUTLET NAME'] = outlet['name']
                    row['OUTLET CODE'] = outlet['code']
                    row['FWP NAME'] = fwp['name']
                    row['FWP CODE'] = fwp['code']
                    row['Competition Brand'] = cols[str(row['brands'])]
                    row['Offered Brand'] = cols[str(row['offer_brand'])]
                    row['CITY'] = cols[str(row['city_id'])]
                    
                    row['coardinates'] = 'Lat : '+str(row['coardinates']['latitude'])+', Long : '+str(row['coardinates']['longitude'])
                    row['signature'] = app.config['DOC_URL']+"signature/download/"+row['signature'].replace("uploads/signature/","")
                except:
                    pass
                
                
                
                #row['outlet_id'] = self.getOutlet(row['outlet_id'])
                data.append(row)
            
            #print(data);
            #self.path = "/usr/local/var/www/pma/uploads/reports/"   
            #self.path = "/var/www/pmitest.redtons.com/uploads/reports/"
            #self.path = "/usr/share/www/pmiLive/uploads/reports/"
            
            
            self.path = app.config['UPLOAD_FOLDER']+"reports/"
            
            id = ObjectId()
            name = 'FormData-'+str(id)+'.xlsx'
            filename = self.path+name   
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            
            
            df1 = pd.DataFrame(data) 
            
            del data
            
            #print(df1.info())
            #print(df1)
            df1.to_excel(writer, sheet_name="FormData",index=False)
                
            writer.save()
            path = "../"+app.config['UPLOAD_FOLDER']+'reports/'+name
            return send_file(path, as_attachment=True)
            # ~ return {'status':'Ok','filename':name},200
            
        
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong : "+str(e)}},400
    
    def getUserId(self,code):
        try:
            user = mongo.db.users.find_one({'code':code})
            if user:
                return user['_id']
            else:
                return False
            
        except:
            return False
    
    def getOutletId(self,code):
        try:
            outlet = mongo.db.outlet.find_one({'code':code})
            if outlet:
                return outlet['_id']
            else:
                return False
            
        except:
            return False
            
    def getUser(self,id):
        row = mongo.db.users.find_one({'_id':getId(id)})
        if row:
            return row['name'];
        return 'None'
    
    def getOutlet(self,id):
        row = mongo.db.outlet.find_one({'_id':getId(id)})
        if row:
            return row['name'];
        return 'None'
 
 
 
@apiV1.resource('/signature/download/<filename>')
class SignatureDownload(Resource):
    def get(self,filename):
        try:
            path = "../"+app.config['UPLOAD_FOLDER']+'signature/'+filename
            return send_file(path, as_attachment=True)
        except:
            return {'error':{"message":"Something Wrong."}},400   
    
