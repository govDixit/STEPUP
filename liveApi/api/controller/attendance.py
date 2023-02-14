from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from flask_jwt_extended import get_jwt_identity
from datetime import date,datetime
from bson import ObjectId


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
    decorators = [check_permissions]
    
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
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
   
    def post(self):
        attendanceLib = AttendanceLib()
        return attendanceLib.markAttendance()
           
  
@apiV1.resource('/supervisor/checkin/<attendance_id>')
class SupervisorList(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'date': {'type': 'string','empty': False,'required':True},
                                'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
        self.delete_fields = {'attendance_checkin_id': {'type': 'string','empty': False,'required':True},
                              'date': {'type': 'string','empty': False,'required':True},
                                'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
        
        self.id = datetime.timestamp(datetime.now())
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        self.checkin_data = { "id" : self.id,
                               "start" : {"date": None,"coardinates" : None},
                               "end" : {"date": None,"coardinates" : None},
                               "selfie" : None,
                            }
        self.checkout_data = {"date": None,"coardinates" : None}
   
    def post(self, attendance_id):
        v = Validator(self.create_fields,allow_unknown=False)
        json = request.get_json()
        # ~ app.logger.info(json) 
        # ~ app.logger.info(attendance_id)  
        if v.validate(json):
            check_in = json['date']
            checkin_id_dt_obj = datetime.strptime(check_in, '%Y-%m-%d %H:%M:%S')
            temp_id = ObjectId.from_datetime(checkin_id_dt_obj)
               
            self.checkin_data['id'] = temp_id
            self.checkin_data['start']['date'] = checkin_id_dt_obj
            # ~ self.checkin_data['start']['date'] = json['date']
            self.checkin_data['start']['coardinates'] = json['coardinates']
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
          
            myquery = {"_id":getId(attendance_id), "date":self.dateInput}
           
            newvalues = {"$set":{"checkin":1},"$addToSet": {"supervisor_checkin_activity" : self.checkin_data}}
          
            r = mongo.db.attendance.update_one(myquery, newvalues)
            #mongo.db.outlet_assign.update_one(myquery, newvalues)
            
            if r.matched_count > 0:
                return {'status':'ok', 'attendance_checkin_id':str(check_in)},201
            else:
                return {'error':{"message":"Attendance Id is not valid in a date."}},400
        else:
            return {'error':v.errors, "date": str(date.today())},400
    
    def delete(self, attendance_id):
        try:
            v = Validator(self.delete_fields,allow_unknown=False)
            json = request.get_json()
            
            if v.validate(json):
                checkin_id = json['attendance_checkin_id'];
                checkin_id_dt_obj = datetime.strptime(checkin_id, '%Y-%m-%d %H:%M:%S')
                checkin_id = ObjectId.from_datetime(checkin_id_dt_obj)
                
                self.checkout_data['date'] = datetime.strptime(json['date'], '%Y-%m-%d %H:%M:%S')
                self.checkout_data['coardinates'] = json['coardinates']
                
                self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
                
                myquery = {"_id":getId(attendance_id),"date":self.dateInput,"supervisor_checkin_activity.id":checkin_id}
                
                newvalues = {"$set": {"checkin":0,"supervisor_checkin_activity.$.end":self.checkout_data}}
           
                r = mongo.db.attendance.update_one(myquery, newvalues) 
                
                if r.matched_count > 0:
                    return {'status':'ok'},200
                else:
                    return {'error':{"message":"Attendance Checkin Id is not valid."}},400
            
            else:
                return {'error':v.errors},400
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400       
        
        
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
                json['duration'] = int(0)
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
            result = mongo.db.outlet_activity.find(query)
            for row in result:
                #if row['end_time'] > hour:
                return row['meeting']
            
            return "Not Assigned"
        except Exception as e:
            print(e)
            return "Not Assigned"
        
        
  
