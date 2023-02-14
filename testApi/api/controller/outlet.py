from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getRow,getId,getCurrentUser
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
from bson import ObjectId
from api.lib.outletLib import OutletLib
import hashlib 
from bson.int64 import Int64
import os
import base64
import pandas as pd
from io import StringIO
from bson import ObjectId
import xlsxwriter
from collections import defaultdict


@apiV1.resource('/outlet/<id>')
class Outlet(Resource):
    
    def __init__(self):
        self.update_fields = {'name': {'type': 'string','empty': False},
                              'area': {'type': 'string','empty': False},
                              'zone': {'type': 'string','empty': False},
                              'address': {'type': 'string','empty': False},
                              'coardinates': {'type': 'dict',
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              },
                              'status': {'type':'number','allowed': [0, 1]},
                              'isVerified': {'type':'number','allowed': [0, 1]},
                              'type': {'type':'string','allowed': ['RETAIL','MTO','LAMP']},
                              'city_id': {'type':'string','empty': False}}
        
    def get(self,id):
        try:
            result = mongo.db.outlet.find_one_or_404({"_id":getId(id)})
            return getData(result),200
        except:
                return {'error':{"message":"Something Wrong"}},400
    
    def put(self,id):
        try:
            v = Validator(self.update_fields,allow_unknown=False)
            json = request.get_json()
            
            json['coardinates']['latitude'] = float(json['coardinates']['latitude'])
            json['coardinates']['longitude'] = float(json['coardinates']['longitude'])
                
            if v.validate(json):
                if "city_id" in json:
                    json['city_id'] = getId(json['city_id'])
                    if not json['city_id']:
                        return {'error':{'city_id':"City Id is not a valid."}},400
                
                mongo.db.outlet.find_one_or_404({"_id":getId(id)})
                
                myquery = {"_id":getId(id)}
                newvalues = {"$set": json}
                
                mongo.db.outlet.update_one(myquery, newvalues)
                
                result = mongo.db.outlet.find_one_or_404({"_id":getId(id)})
                return getData(result),200
            else:
                return {'error':v.errors},400
        except Exception as e:
            return {'error':{"message1":str(e)}},400
        
    def delete(self,id):
        
        mongo.db.outlet.find_one_or_404({"_id":getId(id)})
        
        myquery = {"_id":getId(id)}
        newvalues = {"$set": {"status":3}}
        
        mongo.db.outlet.update_one(myquery, newvalues)
        
        return {'status':'ok'},202
           
           
           
@apiV1.resource('/outlet')
class OutletList(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'type': 'string','required': True,'empty': False},
                              'name': {'type': 'string','required': True,'empty': False},
                              'code': {'type': 'string','required': True,'empty': False},
                              'area': {'type': 'string','required': True,'empty': False},
                              'zone': {'type': 'string','required': True,'empty': False},
                              'address': {'type': 'string','required': True,'empty': False},
                              'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              },
                              'status': {'type':'number','required': True,'allowed': [0, 1]},
                              'isVerified': {'type':'number','allowed': [0, 1]},
                              'type': {'type':'string','allowed': ['RETAIL','MTO','LAMP']}}
        
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
            
            # City Manager Filter    
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])
                
            #print(query)    
            result = mongo.db.outlet.find(query).skip(start).limit(length).sort([('status', -1),('isVerified', -1)])
                
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
            json['coardinates']['latitude'] = float(json['coardinates']['latitude'])
            json['coardinates']['longitude'] = float(json['coardinates']['longitude'])
                
            if v.validate(json):
                json['city_id'] = getId(json['city_id'])
                if not json['city_id']:
                    return {'error':{'city_id':"City Id is not a valid."}},400
                
                json['profile_pic'] = "user.png"
                
                
                id = mongo.db.outlet.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["Outlet already exist."]}},400
        except:
            return {'error':{"message":"Something Wrong"}},400
           


@apiV1.resource('/outlet/today')
class OutletToday(Resource):
    
    def get(self):
        try:
            user = getCurrentUser() 
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
           
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            #self.dateInput = datetime.strptime("2020-07-23","%Y-%m-%d")
            
            
            if user['role'] == 1:
                aggr.append({"$match":{"fwp_id":getId(user['user_id']),"date":self.dateInput}})
            elif user['role'] == 2:
                aggr.append({"$match":{"supervisor_id":getId(user['user_id']),"date":self.dateInput}})
            elif user['role'] == 3:
                aggr.append({"$match":{"citymanager_id":getId(user['user_id']),"date":self.dateInput}})
            
            result = mongo.db.outlet_activity.aggregate(aggr)
            
            hour = datetime.now().hour
           
            temp = []
            if result:   
                for row in result:
                    row['end_time'] = 24
                    if row['status'] == 1:
                        row['outlet']['activity_id'] = row['_id']
                        row['outlet']['checkin'] = row['checkin']
                        row['outlet']['checkin_id'] = row['checkin_id']
                        row['outlet']['selfie'] = row['selfie']
                        row['outlet']['break'] = row['break']
                        row['outlet']['break_id'] = row['break_id']
                        row['outlet']['fwp_id'] = row['fwp_id']
                        row['outlet']['supervisor_id'] = row['supervisor_id']
                        row['outlet']['citymanager_id'] = row['citymanager_id']
                        
                        if row['outlet']['isVerified'] == 0:
                            row['outlet']['outlet_bypass'] = 1;
                            row['outlet']['form_bypass'] = 1;
                        else:
                            row['outlet']['outlet_bypass'] = 0;
                            row['outlet']['form_bypass'] = 0;
                            
                        row['outlet']['vradius'] = 100;
                        row['outlet']['timeout'] = 10*60;
                       
                        if user['role'] == 1:
                            return getData(row['outlet']),200
                        else:
                            temp.append(getData(row['outlet']))
                
                if user['role'] == 1 and len(temp) == 0:
                    return {'error':{"message":"Outlet is not found"}},404    
                else: 
                    return temp,200
            else:
                return {'error':{"message":"Outlet is not found"}},404
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400


        
@apiV1.resource('/outlet/today/<user_id>')
class OutletTodayByUser(Resource):
    
    def get(self,user_id):
        try:
            outletLib = OutletLib()
            user = outletLib.userIdValidate(user_id)
            
            if not user:
                return outletLib.userIdError
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            if user['role'] == 1:
                aggr.append({"$match":{"fwp_id":getId(user_id),"date":self.dateInput}})
            elif user['role'] == 2:
                aggr.append({"$match":{"supervisor_id":getId(user_id),"date":self.dateInput}})
            elif user['role'] == 3:
                aggr.append({"$match":{"citymanager_id":getId(user_id),"date":self.dateInput}})
          
            result = mongo.db.outlet_activity.aggregate(aggr)
            
            temp = []
            if result:   
                for row in result:
                    row['outlet']['checkin'] = row['checkin']
                    row['outlet']['selfie'] = row['selfie']
                    row['outlet']['fwp_id'] = row['fwp_id']
                    row['outlet']['supervisor_id'] = row['supervisor_id']
                    row['outlet']['citymanager_id'] = row['citymanager_id']
                    
                    if user['role'] == 1:
                        return getData(row['outlet']),200
                    else:
                        temp.append(getData(row['outlet']))
                        
                return temp,200
            else:
                return {'error':{"message":"Outlet is not found"}},404
            
        except Exception as e:
            return {'error':{"message":"Something Wrong"}},400
          
        
    

@apiV1.resource('/outlet/assign')
class OutletAssign(Resource):
    
    def __init__(self):
        self.create_fields = {'user_id': {'type': 'string','required': True,'empty': False},
                              'outlet_id': {'type': 'string','required': True,'empty': False},
                              'start_time': {'type': 'number','required': True,'empty': False},
                              'end_time': {'type': 'number','required': True,'empty': False},
                              'meeting': {'type': 'string','required': True,'empty': False},
                              'activity': {'type': 'string','required': True,'empty': False},
                              'cycle': {'type': 'string','required': True,'empty': False},
                              'tse': {'type': 'string','required': True,'empty': False},
                              'asm': {'type': 'string','required': True,'empty': False},
                              'contact': {'type': 'number','required': True,'empty': False},
                              'community': {'type': 'string','required': True,'empty': False}}
        
    
        #self.activity_fields = {"checkin" :None,"break":None,"verifiy":None}
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
                #self.__isChildUser(json['user_id'])
                outletLib = OutletLib()
                hr = outletLib.getHierarchy(json['user_id'])
                
                if not hr:
                    return {'error':{"message":"User Id is not a valid."}},400
                elif not outletLib.outletIdValidate(json['outlet_id']):
                    return {'error':{"message":"Outlet Id is not a valid."}},400
                
                if hr:
                    hr['_id'] = ObjectId()
                    hr['outlet_id'] = getId(json['outlet_id'])
                    hr['date'] = datetime.strptime(str(date.today()),"%Y-%m-%d")
                    hr['outlet_id'] = getId(json['outlet_id'])
                    hr['start_time'] = json['start_time']
                    hr['end_time'] = json['end_time']
                    hr['meeting'] = json['meeting']
                    hr['activity'] = json['activity']
                    hr['cycle'] = json['cycle']
                    hr['tse'] = json['tse']
                    hr['asm'] = json['asm']
                    hr['contact'] = json['contact']
                    hr['community'] = json['community']
                    hr['status'] = 1
                    hr['checkin'] = 0
                    hr['checkin_id'] = None
                    hr['selfie'] = 0
                    hr['break'] = 0
                    hr['break_id'] = None
                    hr['checkin_activity'] = []
                    hr['break_activity'] = []
                    #hr['verify_activity'] = []
                    hr['created_at'] = datetime.now()
                    
                    mongo.db.today_outlet.find_one_and_update({"outlet_id": hr['outlet_id'],"fwp_id":hr['fwp_id'],"date":hr['date']},{"$set":  hr},upsert=True)
                    #mongo.db.outlet_assign.find_one_and_update({"outlet_id": hr['outlet_id'],"date":hr['date']},{"$set":  hr},upsert=True)
                    mongo.db.outlet_activity.find_one_and_update({"outlet_id": hr['outlet_id'],"fwp_id":hr['fwp_id'],"date":hr['date']},{"$set":  hr},upsert=True)
                    #mongo.db.outlet_assign.insert(temp)
                    
                return {'status':'ok'},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":"Outlet already assigned to User."}},400
        except:
            return {'error':{"message":"Something wrong"}},400
    

    """
    
    def put(self):
        outlets = mongo.db.outlet.find()
        outletLib = OutletLib()
        
        try:        
            for row in outlets:
                user = self.getUser(row['code'])
                if user:
                    #print(row)
                    hr = outletLib.getHierarchy(str(user['_id']))
                    #print(hr)
                    hr['outlet_id'] = row['_id']
                    hr['date'] = datetime.strptime(str(date.today() + timedelta(days=0)),"%Y-%m-%d")
                    hr['checkin'] = 0
                    hr['checkin_id'] = None
                    hr['selfie'] = 0
                    hr['break'] = 0
                    hr['break_id'] = None
                    hr['checkin_activity'] = []
                    hr['break_activity'] = []
                    #hr['verify_activity'] = []
                    hr['created_at'] = datetime.now()
                    
                    #print(hr)
                    mongo.db.today_outlet.find_one_and_update({"outlet_id": hr['outlet_id'],"date":hr['date']},{"$set":  hr},upsert=True)
                    #mongo.db.outlet_assign.find_one_and_update({"outlet_id": hr['outlet_id'],"date":hr['date']},{"$set":  hr},upsert=True)
                    mongo.db.outlet_activity.find_one_and_update({"outlet_id": hr['outlet_id'],"date":hr['date']},{"$set":  hr},upsert=True)
        except Exception as e:
            print(e)    """
    
    def getUser(self,code):
        user = mongo.db.users.find_one({"code":code})
        return user
    
    
    def put1(self):
        self.__insertCityManager()
        return {'status':'ok'},201
    
    def __insertCityManager(self):
        
        try:
            code = "101"
            user = {}
            user['code'] = code
            user['name'] = "City Manager "+code
            user['email'] = code+"@gmail.com"
            p = code+code
            user['password'] = hashlib.md5(p.encode()).hexdigest()
            user['mobile'] = Int64(code)
            user['status'] = 1
            user['profile_pic'] = "user.png"
            user['parent_id'] = None
            user['role'] = 3
            id = mongo.db.users.insert(user)
            
            self.__insertSupervisor(getId(id))
            print(id)
                
        except Exception as e:
            print(e)
            
    def __insertSupervisor(self,parent_id):
        
        try:
            for x in range(2,4):
                code = "10"+str(x)
                user = {}
                user['code'] = code
                user['name'] = "Supervisor "+code
                user['email'] = code+"@gmail.com"
                p = code+code
                user['password'] = hashlib.md5(p.encode()).hexdigest()
                user['mobile'] = Int64(code)
                user['status'] = 1
                user['profile_pic'] = "user.png"
                user['parent_id'] = getId(parent_id)
                user['role'] = 2
                id = mongo.db.users.insert(user)
                
                self.__insertFWP(getId(id),x)
                print(id)
                
        except Exception as e:
            print(e)
            
    def __insertFWP(self,parent_id,c):
        
        try:
            for x in range(1,3):
                code = str(c)+"00"+str(x)
                user = {}
                user['code'] = code
                user['name'] = "FWP "+code
                user['email'] = code+"@gmail.com"
                p = code+code
                user['password'] = hashlib.md5(p.encode()).hexdigest()
                user['mobile'] = Int64(code)
                user['status'] = 1
                user['profile_pic'] = "user.png"
                user['parent_id'] = getId(parent_id)
                user['role'] = 1
                id = mongo.db.users.insert(user)
                print(id)
                
        except Exception as e:
            print(e)
        
    
    
    
    
    
    
    
    
    
    
    
    
@apiV1.resource('/outlet/import')
class OutletImport(Resource):
    
    def post(self):
        try:
            json = request.get_json()
            city_id = getId(json['city_id'])
            outlets = json['outlet']
            outlets = outlets.split(',')[1]
            #outlets = outlets.replace("data:text/csv;base64,", "")
           
            code_string = base64.b64decode(outlets)
            #code_string = base64.b64decode(outlets+"=")
            code_string = code_string.decode('utf-8',errors="ignore")
            
            
            TESTDATA = StringIO(code_string)
            df = pd.read_csv(TESTDATA, sep=",")
            
            #print(df)
            #return {'status':'ok'},201
            
            for index, row in df.iterrows():
                t = {}
                t['city_id'] = city_id
                t['name'] = row['name']
                t['code'] = row['code']
                t['area'] = row['area']
                t['zone'] = row['zone']
                t['address'] = row['address']
                t['type'] = row['type']
                t['isVerified'] = 0 #row['isVerified']
                t['coardinates'] = {'latitude':float(row['lat']),'longitude':float(row['long'])}
                t['status'] = 1
                t['profile_pic'] = "user.png"
                mongo.db.outlet.insert(t)
             
            return {'status':'ok'},201
        
        except DuplicateKeyError:
            return {'error':{"message":["Outlet already exist."]}},400
        except Exception as e:
            print(e)
            return {'error':{"message":["Something wrong."]}},400
            
    

@apiV1.resource('/outlet/route/import')
class OutletRoute(Resource):
    
    def __init__(self):
        self.supervisor_ids = []
        self.supervisors = {}
        
        self.fwp_ids = []
        self.fwp = {}
        
        self.outlet_ids = []
        self.outlets = {}
        
        self.user = getCurrentUser() 
        
    def post(self):
        try:
            json = request.get_json()
            #city_id = json['city_id']
            outlets = json['outlet']
            outlets = outlets.split(',')[1]
            #print(outlets)
            #outlets = outlets.replace("data:text/csv;base64,", "")
            #outlets = outlets.replace("data:application/vnd.ms-excel;", "")
            #print(outlets)
            code_string = base64.b64decode(outlets)
            code_string = code_string.decode('utf-8',errors="ignore")
            
            TESTDATA = StringIO(code_string)
            df = pd.read_csv(TESTDATA, sep=",")
            #print(df)
            #return {'data':[],'status':'invalid'},200
            
            supervisor_codes = []
            fwp_codes = []
            outlet_codes = []
            
            for index, row in df.iterrows():
                supervisor_codes.append(str(row['SUPERVISOR']).strip())
                fwp_codes.append(str(row['FWP']).strip())
                outlet_codes.append(str(row['OUTLET']).strip())
                
            self.__getSupervisorIds(supervisor_codes)
            self.__getFWPIds(fwp_codes)
            self.__getOutletIds(outlet_codes)
            
            #print(self.outlets)
            
            invalid_data = []  
            valid_data = []
            
            for index, row in df.iterrows():
                t = {}
                dateInput = datetime.strptime(row['DATE'], '%d/%m/%Y')
                
                if dateInput < datetime.strptime(str(date.today()), '%Y-%m-%d'):
                    t['DATE'] = {'date':str(dateInput).replace(" 00:00:00", ""),'valid':'NO'}
                else:
                    t['DATE'] = {'date':str(dateInput).replace(" 00:00:00", ""),'valid':'YES'}
                #t['DATE'] = str(date).replace(" 00:00:00", "")
                t['OUTLET'] = {'name':'','code':row['OUTLET'],'valid':'NO'}
                t['ACTIVITY'] = row['ACTIVITY']
                t['SUPERVISOR'] = {'name':'','code':row['SUPERVISOR'],'valid':'NO'}
                t['FWP'] = {'name':'','code':row['FWP'],'valid':'NO'}
                t['MEETING'] = row['MEETING']
                #t['VALID'] = 'NO'
                
                isValid = True
                outlet_id = None
                fwp_id = None
                supervisor_id = None
                citymanager_id = None
                
                if str(row['SUPERVISOR']).strip() in self.supervisors:
                    supervisor_id = self.supervisors[str(row['SUPERVISOR']).strip()]['id']
                    citymanager_id = self.supervisors[str(row['SUPERVISOR']).strip()]['parent_id']
                    t['SUPERVISOR']['name'] =  self.supervisors[str(row['SUPERVISOR']).strip()]['name']
                    t['SUPERVISOR']['valid'] = 'YES'
                
                if str(row['FWP']).strip() in self.fwp:
                    fwp_id = self.fwp[str(row['FWP'])]['id']
                    
                    if str(self.fwp[str(row['FWP']).strip()]['parent_id']) == str(supervisor_id):
                        t['FWP']['name'] =  self.fwp[str(row['FWP']).strip()]['name']
                        t['FWP']['valid'] = 'YES'
                    
                    
                if str(row['OUTLET']) in self.outlets:
                    outlet_id = self.outlets[str(row['OUTLET']).strip()]['id']
                    t['OUTLET']['name'] =  self.outlets[str(row['OUTLET']).strip()]['name']
                    t['OUTLET']['valid'] = 'YES'
                
                
                #print(t)
                if t['SUPERVISOR']['valid'] == 'NO' or t['FWP']['valid'] == 'NO' or t['OUTLET']['valid'] == 'NO' or t['DATE']['valid'] == 'NO':
                    invalid_data.append(t)
                    isValid = False
                elif isValid:
                    t = {}
                    t['date'] = dateInput
                    t['outlet_id'] = outlet_id
                    t['fwp_id'] = fwp_id
                    t['supervisor_id'] = supervisor_id
                    t['citymanager_id'] = citymanager_id
                    t['start_time'] = int(row['STARTTIME'])
                    t['end_time'] = int(row['ENDTIME'])
                    t['meeting'] = row['MEETING']
                    t['activity'] = str(row['ACTIVITY']).strip().upper()
                    t['cycle'] = row['CYCLE']
                    t['tse'] = row['TSE']
                    t['asm'] = row['ASM']
                    t['contact'] = row['CONTACT']
                    t['community'] = row['COMMUNITY']
                    t['status'] = row['STATUS']
                    valid_data.append(t)
                    
            
            if len(invalid_data) > 0:
                return {'data':invalid_data,'status':'invalid'},200
            else:
                self.__outletAssign(valid_data)
                return {'status':'ok'},201
            
            
        except DuplicateKeyError:
            return {'error':{"message":["Outlet already assigned."]}},400
        except Exception as e:
            print(e)
            return {'error':{"message":["Something wrong. "+str(e)]}},400
            
    
    
    def __outletAssign(self,data):
        for row in data:
            try:
                row['_id'] = ObjectId()
                row['checkin'] = 0
                row['checkin_id'] = None
                row['selfie'] = 0
                row['break'] = 0
                row['break_id'] = None
                row['checkin_activity'] = []
                row['break_activity'] = []
                row['created_at'] = datetime.now()
                
                mongo.db.today_outlet.find_one_and_update({"outlet_id": row['outlet_id'],"fwp_id":row['fwp_id'],"date":row['date']},{"$set":  row},upsert=True)
                mongo.db.outlet_activity.find_one_and_update({"outlet_id": row['outlet_id'],"fwp_id":row['fwp_id'],"date":row['date']},{"$set":  row},upsert=True)
                      
            except:
                return False 
                        
    def __getSupervisorIds(self,codes):
        try:
            query = {}
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])
                
            query['code'] = {"$in":codes}
            
            users = mongo.db.users.find(query)
            for row in users:
                self.supervisor_ids.append(row['_id'])     
                self.supervisors[str(row['code'])] = {'id':row['_id'],'name':row['name'],'parent_id':row['parent_id']}
        except:
            return False 
    
    def __getFWPIds(self,codes):
        try:
            query = {}
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])
                
            query['code'] = {"$in":codes}
            
            users = mongo.db.users.find(query)
            for row in users:
                self.fwp_ids.append(row['_id'])     
                self.fwp[str(row['code'])] = {'id':row['_id'],'name':row['name'],'parent_id':row['parent_id']}
        except:
            return False 
    
    def __getOutletIds(self,codes):
        try:
            query = {}
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])
                
            query['code'] = {"$in":codes}
           
            users = mongo.db.outlet.find(query)
            for row in users:
                self.outlet_ids.append(row['_id'])     
                self.outlets[str(row['code'])] = {'id':row['_id'],'name':row['name']}
        except:
            return False 
        
        




@apiV1.resource('/outlet/export')
class OutletExport(Resource):
    def __init__(self):
        self.roles = {1:'FWP',2:'SUPERVISOR',3:'CITY MANAGER',4:'IPM'}
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
                
            
            result = mongo.db.outlet.find(query)
            #print(query)
            
            
            
            # Create a workbook and add a worksheet.
            self.path = app.config['UPLOAD_FOLDER']+"reports/"
            
            id = ObjectId()
            name = 'Outlets-'+str(id)+'.xlsx'
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
            worksheet.write(c,1,'TOTAL OUTLETS',header_format)
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
        
        format1 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
       
        worksheet.write(c,0,'NAME',header_format)
        worksheet.write(c,1,'CODE',header_format)
        worksheet.write(c,2,'AREA',header_format)
        worksheet.write(c,3,'ZONE',header_format)
        worksheet.write(c,4,'ADDRESS',header_format)
        worksheet.write(c,5,'LAT',header_format)
        worksheet.write(c,6,'LONG',header_format)
        worksheet.write(c,7,'TYPE',header_format)
        worksheet.write(c,8,'IsVerified',header_format)
        worksheet.write(c,9,'STATUS',header_format)
        
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
       
        worksheet.write(c,0,row['name'])
        worksheet.write(c,1,row['code'])
        worksheet.write(c,2,row['area'])
        worksheet.write(c,3,row['zone'])
        worksheet.write(c,4,row['address'])
        worksheet.write(c,5,row['coardinates']['latitude'])
        worksheet.write(c,6,row['coardinates']['longitude'])
        worksheet.write(c,7,row['type'])
        worksheet.write(c,8,row['isVerified'])
        worksheet.write(c,9,self.status[row['status']])
        
        
        
        
                
     
             
