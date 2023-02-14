from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from flask_jwt_extended import get_jwt_identity
from datetime import date,datetime



@apiV1.resource('/attendance/<user_id>')
class AttendanceByUser(Resource):
    
    def __init__(self):
        self.create_fields = {'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
    def get(self,user_id):
        try:
            result = mongo.db.attendance.find({"user_id":getId(user_id)})
            return getData(result),200    
        except:
            return {'error':{"message":"Something Wrong"}},400     
 
    def post(self,user_id):
        if user_id == get_jwt_identity():
            attendanceLib = AttendanceLib()
            return attendanceLib.markAttendance()
        else:
            return {'error':{"message":"You are not authorized for mark attendance."}},400  
    
    
           
@apiV1.resource('/attendance/<user_id>/<date>')
class AttendanceByUserDate(Resource):
   
    def get(self,user_id,date):
              
        attendanceLib = AttendanceLib()
        
        user_id = getId(user_id)
        if not user_id:
            return attendanceLib.userIdError
        
        date = attendanceLib.dateValidate(date)
        if not date:
            return attendanceLib.dateError
        
        result = mongo.db.attendance.find_one({'user_id':getId(user_id),'date':date})

        if result:
            return getData(result),200    
        else:
            return {'error':{"message":"User is not present."}},404
  
 
 


@apiV1.resource('/attendance/today')
class AttendanceToday(Resource):
    
    def get(self):
        try:
            attendanceLib = AttendanceLib()
            meeting = attendanceLib.getTodayMeetingPoint()
            if attendanceLib.todayAttendance():
                return {'present':1,'address':meeting},200
            else:
                return {'present':0,'address':meeting},200
        except:
            return {'error':{"message":"Something Wrong."}},400
            
              
@apiV1.resource('/attendance/mark')
class AttendanceList(Resource):
    
    def __init__(self):
        self.create_fields = {'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
   
    def post(self):
        attendanceLib = AttendanceLib()
        return attendanceLib.markAttendance()
           
  

class AttendanceLib:
    def __init__(self):
        self.create_fields = {'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
        self.dateError = {'error':{"message":"Date format is not a valid."}},400  
        self.userIdError = {'error':{"message":"User Id is not a valid."}},400  
    
    def todayAttendance(self):
        user_id = get_jwt_identity()
        today_date = datetime.strptime(str(date.today()),"%Y-%m-%d")
        
        result = mongo.db.attendance.find_one({'user_id':getId(user_id),'date':today_date})
        
        if result:
            return True
        else:
            return False
        
        
            
    def markAttendance(self):
        try:
            user_id = get_jwt_identity()
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
                
                json['user_id'] = getId(user_id)
                json['date'] = datetime.strptime(str(date.today()),"%Y-%m-%d")
                json['created_at'] = datetime.now()
                json['address'] = "Noida"
                id = mongo.db.attendance.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":"You have already marked today attendance."}},400  
        
    def dateValidate(self,date):
        try:
            return datetime.strptime(date,"%Y-%m-%d")
        except:
            return False
        
    def getTodayMeetingPoint(self):
        try:
            hour = datetime.now().hour
            
            user = getCurrentUser() 
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            query = {}
            if user['role'] == 1:
                query = {"fwp_id":getId(user['user_id']),"date":self.dateInput}
            elif user['role'] == 2:
                query = {"supervisor_id":getId(user['user_id']),"date":self.dateInput}
           
            #print(query)
            result = mongo.db.today_outlet.find(query)
            for row in result:
                if row['end_time'] > hour:
                    return row['meeting']
            
            return "Not Assigned"
        except Exception as e:
            print(e)
            return "Not Assigned"
        
        
  