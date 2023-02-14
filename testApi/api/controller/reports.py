from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getRow,getId,getCurrentUserId, dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter


@apiV1.resource('/report/download/<filename>')
class ReportDownload(Resource):
    def get(self,filename):
    # ~ def get(self):
        try:
            # ~ filename = request.args.get('filename', '')
            path = "../"+app.config['UPLOAD_FOLDER']+'reports/'+filename
            return send_file(path, as_attachment=True)
        except:
            return {'error':{"message":"Something Wrong."}},400
 



@apiV1.resource('/report/activeOutlet')
class ReportActiveOutlet(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'fromDate': {'required': True,'empty': False}}
        
    
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'ActiveOutlets'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
                row['month'] = row['filter']['fromDate'].strftime("%B")
                
                if str(row['filter']['fromDate']) == str(row['filter']['toDate']):
                    row['date'] = row['filter']['fromDate'].strftime("%d %b, %Y")
                else:
                    row['date'] = row['filter']['fromDate'].strftime("%d %b, %Y") + " To " + row['filter']['toDate'].strftime("%d %b, %Y")
                
                row['created_at'] = row['created_at'].strftime("%d %b, %Y %I:%M:%S %p")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
            
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['fromDate'],"%Y-%m-%d")
                json['fromDate'] = datetime.strptime(json['fromDate'],"%Y-%m-%d")
                json['toDate'] = datetime.strptime(json['toDate'],"%Y-%m-%d")
                
                #city_id = getId(json['city_id'])
                #if city_id == False:
                    #city_id = None
                
                data = {}
                data['name'] = "ActiveOutlets"
                data['filter'] = {'city_id':None,'fromDate':json['fromDate'],'toDate':json['toDate']}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400
        
        
        
        

@apiV1.resource('/report/dashboard')
class Reportdashboard(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'date': {'required': True,'empty': False}}
        
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'Dashboard'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
               
                row['month'] = row['filter']['date'].strftime("%B")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
            
    def post(self):
        
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['date'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
               
                data = {}
                data['name'] = "Dashboard"
                data['filter'] = {'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400







                
@apiV1.resource('/report/attendance')
class ReportAttendance(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'date': {'required': True,'empty': False}}
        
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'Attendance'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
               
                row['month'] = row['filter']['date'].strftime("%B")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
            
    def post(self):
        
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['date'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
               
                data = {}
                data['name'] = "Attendance"
                data['filter'] = {'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400
            
            


@apiV1.resource('/report/stock')
class ReportStock(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'date': {'required': True,'empty': False}}
        
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'Stock'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
               
                row['month'] = row['filter']['date'].strftime("%B")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
            
    def post(self):
        
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['date'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
               
                data = {}
                data['name'] = "Stock"
                data['filter'] = {'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400          
        
        
        
        
        
@apiV1.resource('/report/mip')
class ReportMip(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'date': {'required': True,'empty': False}}
        
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'MIP'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
               
                row['month'] = row['filter']['date'].strftime("%B")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
            
    def post(self):
        
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['date'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
               
                data = {}
                data['name'] = "MIP"
                data['filter'] = {'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400          
  



@apiV1.resource('/report/ecc')
class ReportEcc(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'date': {'required': True,'empty': False}}
        
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'ECC'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
               
                row['month'] = row['filter']['date'].strftime("%B")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
            
    def post(self):
        
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['date'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
               
                data = {}
                data['name'] = "ECC"
                data['filter'] = {'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400    
        
  
@apiV1.resource('/report/productivity')
class ReportProductivity(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': False,'empty': False},
                              'date': {'required': True,'empty': False}}
        
    
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
           
            result = mongo.db.report_requests.find({'name':'Productivity'}).skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            temp = []
            for row in result:
               
                row['month'] = row['filter']['date'].strftime("%B")
                
                del row['filter']
                temp.append(getRow(row))
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
        
            
    def post(self):
        
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['date'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
               
                data = {}
                data['name'] = "Productivity"
                data['filter'] = {'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400          
