from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getRow,getId,getCurrentUser,requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
import os
import base64
import pandas as pd
from io import StringIO
from bson import ObjectId
import xlsxwriter
from collections import defaultdict
from datetime import datetime
from api.controller import city

@apiV1.resource('/city/wd/<id>')
class CityWD(Resource):
    
    def __init__(self):
        self.update_fields = {'city_id': {'type':'string','required': True,'empty': False},
                              'areas': {'type': 'string','required': True,'empty': True},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self,id):
        result = mongo.db.wd_areas.find_one_or_404({"_id":getId(id)})
        
        if result:
            result['areas'] = '\n'.join([str(elem) for elem in result['areas']]) 
            
        return getData(result),200
    
    def put(self,id):
        v = Validator(self.update_fields,allow_unknown=False)
        json = request.get_json()
        if v.validate(json):
            mongo.db.wd_areas.find_one_or_404({"_id":getId(id)})
            
            json['city_id'] = getId(json['city_id'])
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
            
            mongo.db.wd_areas.update_one(myquery, newvalues)
            
            result = mongo.db.wd_areas.find_one_or_404({"_id":getId(id)})
            return getData(result),200
        else:
            return {'error':v.errors},400
        
    def delete(self,id):
        
        mongo.db.wd_areas.find_one_or_404({"_id":getId(id)})
        
        myquery = {"_id":getId(id)}
        newvalues = {"$set": {"status":3}}
        
        mongo.db.city.update_one(myquery, newvalues)
        
        return {'status':'ok'},202
           
           
           
@apiV1.resource('/city/wd')
class CityWDList(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'type':'string','required': True,'empty': False},
                              'name': {'type': 'string','required': True,'empty': False},
                              'areas': {'type': 'string','required': True,'empty': True},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            city_id = request.args.get('city_id','0')
            
            self.user = getCurrentUser()
            # City Manager Filter
            if self.user['role'] == 3:
                data = {"draw":0,"recordsTotal":0,"recordsFiltered":0,"data":[]}
                return data,200
            
            r = mongo.db.city.find()
            city ={}
            for row in r:
                city[row['_id']] = row['name']
            
            query = {}
            if city_id != '0':
                query['city_id'] = getId(city_id)
            if search != '':
                query['$or'] = [{'name':{'$regex' : search, '$options' : 'i'}}]
           
            result = mongo.db.wd_areas.find(query).skip(start).limit(length).sort([('status', -1)])
                
            total = result.count()
            
            temp = []
            for row in result:
                t = {}
                t['id'] = str(row['_id'])
                t['city_id'] = str(row['city_id'])
                t['city'] = city[row['city_id']]
                t['name'] = row['name']
                t['areas'] = row['areas']
               
                temp.append(t)
               
           
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
        except Exception as e:
            return {'error':{"message":"Something Wrong "+str(e)}},400
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            #return json,200
            if v.validate(json):
                json['city_id'] = getId(json['city_id'])
                
                r = mongo.db.wd_areas.find_one({"city_id":json['city_id'],"name":json['name']})
                if r:
                    return {'error':{"message":["WD is already exist."]}},400
                
                area = json['areas']
                tempArea = area.rsplit('\n')
                
                areas = []
                for row in tempArea:
                    row = row.strip()
                    if row != '':
                        areas.append(row.upper())
                
                json['areas'] = areas
                
                
                json['status'] = int(json['status'])
                id = mongo.db.wd_areas.insert(json)
                
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["City already exist."]}},400
           
  



@apiV1.resource('/city/wd/export')
class CityWDExport(Resource):
    def __init__(self):
        self.status = {0:'InActive',1:'Active'}
        self.city = {}
        self._getCity()
    
    def _getCity(self):
        try:
            result =  mongo.db.city.find()
            for row in result:
                self.city[str(row['_id'])] = {'name':row['name'],'total':0}
        except Exception as e:
            return {'error':{"message":"Error " + str(e)}},400        
            
              
    def post(self):
        try:
            json = request.get_json()
            query = {}
            
            json['city_id'] = getId(json['city_id'])
     
            if json['city_id'] != False:
                query['city_id'] = json['city_id']
                
            
            result = mongo.db.wd_areas.find(query)
            #print(query)
            
            
            
            # Create a workbook and add a worksheet.
            self.path = app.config['UPLOAD_FOLDER']+"reports/"
            
            id = ObjectId()
            name = 'WDAREAS-'+str(id)+'.xlsx'
            filename = self.path+name   
            
            
            
            data = defaultdict(lambda: defaultdict(list))
            
            for row in result:
                row = getRow(row)
                data[row['city_id']][row['id']].append(row)
                   
              
            #print(self.fwp)
            workbook = xlsxwriter.Workbook(filename,options={'nan_inf_to_errors': True})
            worksheet = workbook.add_worksheet("SUMMARY")
            
            c = 0
            c = self.__insertCity(c,'CITY',workbook,worksheet,data)
            
            
            header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
            format1 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
            
            c = 0
            worksheet.write(c,0,'CITY NAME',header_format)
            worksheet.write(c,1,'TOTAL WD AREAS',header_format)
            for k in self.city:
                row = self.city[k]
                c += 1
                worksheet.write(c,0,row['name'])
                worksheet.write(c,1,row['total'])
            
            
            worksheet.set_column(0, 4, 25)
            workbook.close()


            return {'status':'Ok','filename':name},200
            
        
        except Exception as e:
            return {'error':{"message":"Error " + str(e)}},400    

    
    
    def __insertCity(self,c,title,workbook,worksheet,data):
        for k in data:
            c = 0
            row = data[k]
            self.city[k]['total'] = len(row)
            worksheet = workbook.add_worksheet(self.city[k]['name'])
            worksheet.set_column(0, 4, 25)
            
            c = self.__insertWorksheet(c,title,workbook,worksheet,row)
        
        
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
        
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'bold': False, 'valign':'vcenter','font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'bold': False, 'valign':'vcenter','font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
       
        worksheet.write(c,0,'NAME',header_format)
        worksheet.write(c,1,'AREAS',header_format)
        worksheet.write(c,2,'STATUS',header_format)
        
        for k in data:
            c += 1
            row = data[k][0]
            self.__insertRow(worksheet,c,row,format1,format2)
            
        return c+2
        
            
    def __insertRow(self,worksheet,c,row,format1,format2):   
        if (c % 2) == 0:  
            worksheet.set_row(c, cell_format=format1)
        else:
            worksheet.set_row(c, cell_format=format2) 
        area = '\n'.join([str(elem) for elem in row['areas']]) 
        worksheet.write(c,0,row['name'])
        worksheet.write(c,1,area)
        worksheet.write(c,2,self.status[row['status']])
        
        
        



@apiV1.resource('/city/wd/select/<city_id>')
class CityWDSelect(Resource): 
    def get(self,city_id):
        try:        
            result = mongo.db.wd_areas.find({"city_id":getId(city_id)})
            
            data = []
            for row in result:
                #data.append({'id':str(row['_id']),'name':row['name']})
                data.append({'id':str(row['_id']),'name':row['name'],'areas':row['areas']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200
        
        
        
        
        
@apiV1.resource('/city/wd/import')
class CityWDImport(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'type':'string','required': True,'empty': False},
                              'data': {'type': 'string','required': True,'empty': False}}
        
    def post(self):
        try:
            
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
            
                city_id = getId(json['city_id'])
                data = json['data']
                data = data.split(',')[1]
                #outlets = outlets.replace("data:text/csv;base64,", "")
               
                code_string = base64.b64decode(data)
                #code_string = base64.b64decode(outlets+"=")
                code_string = code_string.decode('utf-8',errors="ignore")
                
                
                TESTDATA = StringIO(code_string)
                df = pd.read_csv(TESTDATA, sep=",")
                
                #print(df)
                
                wd = {}
                temp = []
                
                for index, row in df.iterrows():
                    if row['WD-DISTRIBUTOR'] in wd:
                        wd[row['WD-DISTRIBUTOR']].append(row['WD-AREA'])
                    else:
                        wd[row['WD-DISTRIBUTOR']] = [row['WD-AREA']]
                        
                for k in wd:
                    t = {}
                    t['city_id'] = city_id
                    t['name'] = k
                    t['areas'] = wd[k]
                    t['status'] = 1
                    t['created_at'] = datetime.now()
                    t['updated_at'] = None
                    
                    mongo.db.wd_areas.find_one_and_update({"city_id":city_id,"name": k},{"$set":t},upsert=True)
                    #mongo.db.wd_areas.insert(t)
               
                return {'status':'ok'},201
            
            else:
                return {'error':v.errors},400
                
        except DuplicateKeyError:
            return {'error':{"message":["Outlet already exist."]}},400
        except Exception as e:
            print(e)
            return {'error':{"message":["Something wrong."]}},400
            
        
           
