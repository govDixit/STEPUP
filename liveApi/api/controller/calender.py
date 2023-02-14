from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from flask_jwt_extended import get_jwt_identity
from datetime import date,datetime,timedelta


    
           
@apiV1.resource('/calender/<user_id>/<date>')
class CalenderByUserDate(Resource):
    decorators = [check_permissions]
    
    def get(self,user_id,date):
        try:
           

            self.dateInput = datetime.strptime(str(date),"%Y-%m-%d")
            
            user = getCurrentUser() 
            
            aggr = [{"$lookup": { "from": "user", "localField": "user_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            
            if user['role'] == 1:
                query = {'fwp_id':getId(user['user_id']),'date':self.dateInput}
            elif user['role'] == 2:
                query = {'supervisor_id':getId(user['user_id']),'date':self.dateInput}
            elif user['role'] == 3:
                query = {'citymanager_id':getId(user['user_id']),'date':self.dateInput}
            else:
                query = {'citymanager_id':getId(user_id),'date':self.dateInput}
            
            #print(query)    
            result = mongo.db.outlet_activity.find(query)
            
            user_ids = []
            users = {}
            
            outlet_ids = []
            outlets = {}
            
            activities = []
            
            for row in result:
                user_ids.append(row['fwp_id'])
                outlet_ids.append(row['outlet_id'])
                activities.append(row)
            
            result = mongo.db.users.find({'_id':{"$in":user_ids}})
            for row in result:
                users[str(row['_id'])] = row['code']
                
            result = mongo.db.outlet.find({'_id':{"$in":outlet_ids}})
            for row in result:
                outlets[str(row['_id'])] = row['code']
            
            temp = []
            for row in activities:
                #print(row)
                t = {}
                t['id'] = str(row['_id'])
                if user['role'] == 1:
                    t['name'] = outlets[str(row['outlet_id'])]
                else:
                    t['name'] = users[str(row['fwp_id'])] + " / " + outlets[str(row['outlet_id'])]
                t['profile_pic'] = ''
                t['address'] = "Meeting Point : "+row['meeting']
                tt = timedelta(0,row['start_time']*60*60)
                last_bus_time = self.dateInput + tt
                
                t['time'] = 0 #last_bus_time.strftime("%I:%M %p")
            
            
                
                temp.append(t)
                
            return temp,200    
            
        except Exception as e:
            print(e)
            return {'error':{"message":["Something wrong."]}},400
  
 
 

