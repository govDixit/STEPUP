from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUserId
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from bson import ObjectId
from api.lib.outletLib import OutletLib



@apiV1.resource('/stock/verification/<user_id>')
class OutletVerification(Resource):
    
    def __init__(self):
        self.create_fields = {'step': {'type':'number','required': True,'allowed': [1, 2,3]},
                              'date': {'type': 'date','empty': False,'required':True},
                              'list': {'type': 'list','required':True},
                              'verify': {'type':'number','required': True,'allowed': [0,1]},
                              'comments': {'type':'string','required': True},
                              'coardinates': {'type': 'dict','required':True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }
                              }
        
        self.id = ObjectId()
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        self.verify_data = {"verify_by" : getId(getCurrentUserId()),
                              "list" : None,
                              "date": None,
                              "coardinates" : None,
                              "selfie" : 0,
                              "verify" : 0,
                              "comments": None,
                            }
        
    
    def post(self,user_id):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            outletLib = OutletLib()
            dateInput = outletLib.dateTimeValidate(json['date'])
            
            json['date'] = dateInput
            
            if v.validate(json):
                #self.verify_data['step'] = json['step']
                #self.verify_data['user_id'] = user_id
                self.verify_data['list'] = json['list']
                self.verify_data['date'] = json['date']
                self.verify_data['coardinates'] = json['coardinates']
                self.verify_data['verify'] = json['verify']
                self.verify_data['comments'] = json['comments']
                
                self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
              
                myquery = {"user_id":getId(user_id),"date":self.dateInput}
                newvalues = {"$set": {"step"+str(json['step'])+"_verify" :1,"step"+str(json['step'])+"_data" : self.verify_data}}
                
                r = mongo.db.stocks.update_one(myquery, newvalues)
               
                if r.matched_count > 0:
                    return {'status':'ok'},201
                else:
                    return {'error':{"message":"Stock / User Id is not valid in a date."}},400
            
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
        
    # upldate checkin selfie
    def put(self,user_id):
        try:
            outletLib = OutletLib()
            filename = outletLib.fileUpload("verification",request.files)
            step = request.form.get('step')
            step = step.replace('"', '')
            step = int(step)
            
            
            if step < 0 or step > 3:
                return {'error':{"message":"Step value is not a valid."}},400
            if not filename:
                return {'error':{"message":"File is not valid."}},400
            
            self.verify_data['selfie'] = filename
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            myquery = {"user_id":getId(user_id),"date":self.dateInput}
            newvalues = {"$set": {"step"+str(step)+"_data.selfie" : filename}}
           
            r = mongo.db.stocks.update_one(myquery, newvalues)
           
            if r.matched_count > 0:
                return {'status':'ok','filename':filename},200
            else:
                return {'error':{"message":"Stock / User Id is not valid in a date."}},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
           
    
        
        