from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from bson import ObjectId
from api.lib.outletLib import OutletLib


@apiV1.resource('/outlet/checkin/<outlet_id>')
class OutletCheckin(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'checkin_id': {'type': 'string','empty': False,'required':False},
                              'activity_id': {'type': 'string','empty': False,'required':False},
                              'date': {'type': 'date','empty': False,'required':True},
                                'coardinates': {'type': 'dict','required':True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }
                              }
        
        self.delete_fields = {'checkin_id': {'type': 'string','empty': False,'required':True},
                              'activity_id': {'type': 'string','empty': False,'required':False},
                              'cc': {'type': 'number','empty': False,'required':True},
                              'date': {'type': 'date','empty': False,'required':True},
                                'coardinates': {'type': 'dict','required':True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }
                              }
        
        self.id = datetime.timestamp(datetime.now())
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        self.checkin_data = { "id" : self.id,
                               "start" : {"date": None,"coardinates" : None},
                               "end" : {"date": None,"coardinates" : None},
                               "selfie" : None,
                            }
        self.checkout_data = {"date": None,"coardinates" : None}
    
    def post(self,outlet_id):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            outletLib = OutletLib()
            dateInput = outletLib.dateTimeValidate(json['date'])
            
            """if not date:
                return {'error':{"message":"Datetime is not a valid format"}},400"""
            json['date'] = dateInput
            
            if v.validate(json):
                if 'checkin_id' in json: 
                    self.id = json['checkin_id'];
                 
                checkin_id_dt_obj = datetime.strptime(self.id, '%Y-%m-%d %H:%M:%S')
    
                #checkin_id_dt_obj = datetime.fromtimestamp(self.id)
                temp_id = ObjectId.from_datetime(checkin_id_dt_obj)
                
                self.checkin_data['id'] = temp_id
                self.checkin_data['start']['date'] = json['date']
                self.checkin_data['start']['coardinates'] = json['coardinates']
                
                self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
              
                myquery = {"outlet_id":getId(outlet_id),"date":self.dateInput}
                
                if 'activity_id' in json: 
                    activity_id = json['activity_id'];
                    myquery = {"_id":getId(activity_id)}
               
                newvalues = {"$set":{"checkin":1,"checkin_id":self.id},"$addToSet": {"checkin_activity" : self.checkin_data}}
              
                mongo.db.today_outlet.update_one(myquery, newvalues)
                #mongo.db.outlet_assign.update_one(myquery, newvalues)
                r = mongo.db.outlet_activity.update_one(myquery, newvalues)
                
                if r.matched_count > 0:
                    return {'status':'ok','checkin_id':str(self.id)},201
                else:
                    return {'error':{"message":"Outlet Id is not valid in a date."}},400
            
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
        
    # upldate checkin selfie
    def put(self,outlet_id):
        try:
            outletLib = OutletLib()
            
            filename = outletLib.fileUpload("checkin",request.files)
            checkin_id = request.form.get('checkin_id');
            checkin_id = checkin_id.replace('"', '')
            
            activity_id = request.form.get('activity_id');
            activity_id = activity_id.replace('"', '')
            
            checkin_id_dt_obj = datetime.strptime(checkin_id, '%Y-%m-%d %H:%M:%S')
            
            #checkin_id_dt_obj = datetime.fromtimestamp(float(checkin_id))
            
            checkin_id = ObjectId.from_datetime(checkin_id_dt_obj)
            
            if not filename:
                return {'error':{"message":"File is not valid."}},400
            
            
            self.checkin_data['selfie'] = filename
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            myquery = {"outlet_id":getId(outlet_id),"date":self.dateInput,"checkin_activity.id":checkin_id}
            
            if activity_id != '': 
                myquery = {"_id":getId(activity_id),"checkin_activity.id":checkin_id}
            #print(myquery)        
            newvalues = {"$set": {"selfie":1,"checkin_activity.$.selfie":filename}}
            
            mongo.db.today_outlet.update_one(myquery, newvalues)
            #mongo.db.outlet_assign.update_one(myquery, newvalues)
            r = mongo.db.outlet_activity.update_one(myquery, newvalues) 
           
            if r.matched_count > 0:
                return {'status':'ok','filename':filename},200
            else:
                return {'error':{"message":"Checkin Id or File are not valid."}},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
           
    def delete(self,outlet_id):
        try:
            v = Validator(self.delete_fields,allow_unknown=False)
            json = request.get_json()
            
            outletLib = OutletLib()
            dateInput = outletLib.dateTimeValidate(json['date'])
            
            """if not date:
                return {'error':{"message":"Datetime is not a valid format"}},400"""
            json['date'] = dateInput
            
            if v.validate(json):
                checkin_id = json['checkin_id'];
                cc = json['cc'];
                
                checkin_id_dt_obj = datetime.strptime(checkin_id, '%Y-%m-%d %H:%M:%S')
                #checkin_id_dt_obj = datetime.fromtimestamp(checkin_id)
                checkin_id = ObjectId.from_datetime(checkin_id_dt_obj)
                
                
                self.checkout_data['date'] = json['date']
                self.checkout_data['coardinates'] = json['coardinates']
                
                self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
                
                myquery = {"outlet_id":getId(outlet_id),"date":self.dateInput,"checkin_activity.id":checkin_id}
                
                if 'activity_id' in json: 
                    activity_id = json['activity_id'];
                    myquery = {"_id":getId(activity_id),"checkin_activity.id":checkin_id}
                    
                newvalues = {"$set": {"cc":cc,"checkin":0,"selfie":0,"checkin_activity.$.end":self.checkout_data}}
           
                mongo.db.today_outlet.update_one(myquery, newvalues)
                #mongo.db.outlet_assign.update_one(myquery, newvalues)
                r = mongo.db.outlet_activity.update_one(myquery, newvalues) 
                
                if r.matched_count > 0:
                    return {'status':'ok'},200
                else:
                    return {'error':{"message":"Checkin Id is not valid."}},400
            
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400       
        
        
        
