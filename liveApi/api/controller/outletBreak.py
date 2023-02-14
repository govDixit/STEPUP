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



@apiV1.resource('/outlet/break/<outlet_id>')
class OutletBreak(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'break_id': {'type': 'string','empty': False,'required':False},
                              'activity_id': {'type': 'string','empty': False,'required':False},
                              'date': {'type': 'date','empty': False,'required':True},
                                'coardinates': {'type': 'dict','required':True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }
                              }
        
        self.delete_fields = {'break_id': {'type': 'string','empty': False,'required':True},
                              'activity_id': {'type': 'string','empty': False,'required':False},
                              'date': {'type': 'date','empty': False,'required':True},
                                'coardinates': {'type': 'dict','required':True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }
                              }
        
        self.id = datetime.timestamp(datetime.now())
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        self.break_data = { "id" : self.id,
                               "start" : {"date": None,"coardinates" : None},
                               "end" : {"date": None,"coardinates" : None}
                            }
        self.breakout_data = {"date": None,"coardinates" : None}
    
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
                if 'break_id' in json: 
                    self.id = json['break_id'];
                
                break_id_dt_obj = datetime.strptime(self.id, '%Y-%m-%d %H:%M:%S')    
                #break_id_dt_obj = datetime.fromtimestamp(self.id)
                temp_id = ObjectId.from_datetime(break_id_dt_obj)
                
                self.break_data['id'] = temp_id
                self.break_data['start']['date'] = json['date']
                self.break_data['start']['coardinates'] = json['coardinates']
                
                self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
                myquery = {"outlet_id":getId(outlet_id),"date":self.dateInput}
                
                if 'activity_id' in json: 
                    activity_id = json['activity_id'];
                    myquery = {"_id":getId(activity_id)}
                    
                newvalues = {"$set":{"break":1,"break_id":self.id},"$addToSet": {"break_activity" : self.break_data}}
              
                mongo.db.today_outlet.update_one(myquery, newvalues)
                #mongo.db.outlet_assign.update_one(myquery, newvalues)
                r = mongo.db.outlet_activity.update_one(myquery, newvalues) 
                
                if r.matched_count > 0:
                    return {'status':'ok','break_id':str(self.id)},201
                else:
                    return {'error':{"message":"Outlet Id is not valid in a date."}},400
            
            else:
                return {'error':v.errors},400
            
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
                break_id = json['break_id'];
                break_id_dt_obj = datetime.strptime(break_id, '%Y-%m-%d %H:%M:%S')    
                #break_id_dt_obj = datetime.fromtimestamp(break_id)
                break_id = ObjectId.from_datetime(break_id_dt_obj)
                
                self.breakout_data['date'] = json['date']
                self.breakout_data['coardinates'] = json['coardinates']
                
                self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
                
                myquery = {"outlet_id":getId(outlet_id),"date":self.dateInput,"break_activity.id":break_id}
                
                if 'activity_id' in json: 
                    activity_id = json['activity_id'];
                    myquery = {"_id":getId(activity_id),"break_activity.id":break_id}
                    
                #print(myquery)    
                newvalues = {"$set": {"break":0,"break_activity.$.end":self.breakout_data}}
           
                mongo.db.today_outlet.update_one(myquery, newvalues)
                #mongo.db.outlet_assign.update_one(myquery, newvalues)
                r = mongo.db.outlet_activity.update_one(myquery, newvalues) 
                
                if r.matched_count > 0:
                    return {'status':'ok'},200
                else:
                    return {'error':{"message":"Break Id is not valid."}},400
            
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400       
        
        
        
