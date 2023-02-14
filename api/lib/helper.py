from api import app
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
            t['start'] = getRow(row['start'])
            t['end'] = getRow(row['end'])
            if 'selfie' in row:
                t['selfie'] = row['selfie']
            temp.append(t)
            
    except Exception as e:
        print(e)
        
    return temp
        
def getRow(row):
    try:
        for k in row.keys(): 
            
            if isinstance(row[k], ObjectId):
                row[k] = str(row[k])
            elif isinstance(row[k], datetime):
                row[k] = str(row[k])
            
            if k == '_id':
                row['id'] = str(row[k])
                row.pop('_id') 
            elif k == "profile_pic":
                row['profile_pic'] =  app.config['BASE_URL']+row['profile_pic']
                
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
 
 
 
 
 
 
 
 