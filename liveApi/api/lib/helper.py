from api import app, mongo
from functools import wraps
from bson import ObjectId
from pymongo.cursor import Cursor
import json
import unicodedata
from flask import request
from datetime import date,datetime
from flask_jwt_extended import get_jwt_identity,get_jwt_claims

          
def getCurrentUser():
    return get_jwt_claims()

def getCurrentUserId():
    return get_jwt_identity()

def check_permissions(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        roles = dict() 
        roles[1] = ['outlettoday', 'formcitybyid', 'graphmenu', 'attendancetoday', 'testpaperbroadcastlist', 'sosnotificationbyid', 'userpic', 'userpasswordreset', 'calenderbyuserdate', 'learning', 'learningread', 'skillslanguage', 'skills', 'graphfwp', 'attendancelist', 'outletnotification', 'chatUserlistbyid', 'outlet', 'outletcheckin', 'miformlist', 'outletbreak', 'skillslist']
        roles[2] = ['graphmenu', 'attendancetoday', 'propuctlist', 'outlettodaybyuser', 'outlettoday', 'outletverification', 'stock', 'userlistbyparent', 'testpaperbroadcastlist', 'sosnotificationbyid', 'userpic', 'userpasswordreset', 'calenderbyuserdate', 'learning', 'learningread', 'testpaperelearninglist', 'skillslanguage', 'skills', 'testpaperskillslist', 'chatuserlistbyid', 'attendancelist', 'supervisorlist', 'graphsupervisor']
        roles[3] = ['graphmenu', 'attendancetoday', 'propuctlist', 'userlistbyparent', 'testpaperbroadcastlist', 'sosnotificationbyid', 'userpic', 'userpasswordreset', 'graphcitymanager', 'outlet', 'chatuserlistbyid', 'stock', 'attendancelist', 'calenderbyuserdate', 'outletverification', 'learning', 'learningread', 'skillslanguage', 'skills','formcitybyid','skillslist', 'miformlist', 'outlet']
        roles[4] = ['graphmenu', 'attendancetoday', 'propuctlist', 'userlistbyparent', 'testpaperbroadcastlist', 'sosnotificationbyid', 'userpic', 'userpasswordreset', 'chatuserlistbyid', 'outlettodaybyuser', 'stock', 'calenderbyuserdate', 'attendancelist', 'graphadmin', 'chatuserlistbyid','skills','formcitybyid','skillslist', 'miformlist', 'outlet']
         
        ## these are the classes that's only use in mobile app
        # ~ roles[5] = ['outlettoday', 'formcitybyid', 'supervisorlist', 'graphsupervisor', 'attendancetoday', 'attendancelist', 'graphmenu', 'propuctlist', 'userlistbyparent', 'testpaperbroadcastlist', 'sosnotificationbyid', 'userpic', 'userpasswordreset', 'graphcitymanager', 'chatuserlistbyid', 'outletcheckin', 'outletbreak', 'outlettodaybyuser', 'outletverification', 'stock', 'calenderbyuserdate', 'graphadmin', 'graphfwp', 'learning', 'learningread', 'skillslanguage']
        
        ## these are the classes that's use in both mobile and browser admin
        roles[5] = ['outlet', 'miformlist', 'skillslist', 'skills']
        current_user = getCurrentUser()
        class_name = request.endpoint
        if current_user:
            try:
                role = current_user['role']
                role_perms = roles[role]
                if class_name not in role_perms:
                    return {'error' : {'message':'You don\'t have permission!'}}, 403
            except:
                return {'error' : {'message':'You don\'t have permission!'}}, 403
        return fn(*args, **kwargs)
    return wrapper

def dateTimeValidate(date):
        try:
            return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except:
            return False
        

def getActivity(data):
    temp = []
    try:
        for row in data:
            t = {}
            t['start'] = getRowNew(row['start'])
            t['end'] = getRowNew(row['end'])
            if 'selfie' in row:
                t['selfie'] = app.config['DOC_URL']+"checkin/download/"+row['selfie']
            temp.append(t)
            
    except Exception as e:
        print(e)
        
    return temp


def getRowNew(row):
    try:
        for k in row.keys(): 
            
            if isinstance(row[k], ObjectId):
                row[k] = str(row[k])
            elif isinstance(row[k], datetime):
                row[k] = str(row[k])
            elif isinstance(row[k], float):
                row[k] = str(row[k])
                
            if k == 'coardinates':
                if 'latitude' in row[k]:
                    row[k]['latitude'] = str(row[k]['latitude'])
                if 'longitude' in row[k]:
                    row[k]['longitude'] = str(row[k]['longitude'])
            
            if k == '_id':
                row['id'] = str(row[k])
                row.pop('_id') 
            elif k == "profile_pic":
                row['profile_pic'] =  app.config['DOC_URL']+"user/pic/"+row['profile_pic'].replace("uploads/profile/","")
                
        return row
    except:
        return ""
      
def getRow(row):
    try:
        for k in row.keys(): 
            
            if isinstance(row[k], ObjectId):
                row[k] = str(row[k])
            elif isinstance(row[k], datetime):
                row[k] = str(row[k]) 
            elif isinstance(row[k], float):
                row[k] = str(row[k])
                
            if k == 'coardinates':
                if 'latitude' in row[k]:
                    row[k]['latitude'] = str(row[k]['latitude'])
                if 'longitude' in row[k]:
                    row[k]['longitude'] = str(row[k]['longitude'])
            
            
            if k == '_id':
                row['id'] = str(row[k])
                row.pop('_id') 
            elif k == "profile_pic":
                row['profile_pic'] =  app.config['DOC_URL']+"user/pic/"+row['profile_pic'].replace("uploads/profile/","")
                
        return row
    except:
        return None

    
def getData(data):
    temp = []
    if isinstance(data, Cursor):
        for row in data:
            temp.append(getRow(row))
        return temp
    else:
        return getRow(data)


def getId(id):
    try:
        return ObjectId(id)
    except:
        return False

def _decode(o):
    # Note the "unicode" part is only for python2
    if isinstance(o, str) or isinstance(o, unicodedata):
        try:
            return int(o)
        except ValueError:
            return o
    elif isinstance(o, dict):
        return {k: _decode(v) for k, v in o.items()}
    elif isinstance(o, list):
        return [_decode(v) for v in o]
    else:
        return o

def requestJsonData():  
    json_data = request.get_json()  
    print(json_data)
    json_data = json.dumps(json_data);
    print(json_data)
    return json.JSONDecoder(json_data)
    
    
    
def _parseJSON(obj):
    newobj = {}

    for key, value in obj.iteritems():
        key = str(key)

        if isinstance(value, dict):
            newobj[key] = _parseJSON(value)
        elif isinstance(value, list):
            if key not in newobj:
                newobj[key] = []
                for i in value:
                    newobj[key].append(_parseJSON(i))
        elif isinstance(value, str):
            val = str(value)
            if val.isdigit():
                val = int(val)
            else:
                try:
                    val = float(val)
                except ValueError:
                    val = str(val)
            newobj[key] = val

    return newobj 
 
class CustomJSONDecoder(json.JSONDecoder):
    def default(self, o):
        return json.loads(o, object_hook=lambda d: {int(v) if v.lstrip('-').isdigit() else v: v for k, v in d.items()})
 
 
 
 
 
 
 
 
