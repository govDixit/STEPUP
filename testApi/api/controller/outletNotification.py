from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUserId, dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta


@apiV1.resource('/outlet/notification/<id>')
class OutletNotification(Resource):
    
    def __init__(self):
        self.create_fields = {'date': {'type': 'date','empty': False,'required':True},
                              'coardinates': {'type': 'dict',
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
    
    def post(self,id):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            json['date'] = dateTimeValidate(json['date'])
            if v.validate(json):
                json['outlet_id'] = getId(id)
                json['user_id'] = getId(getCurrentUserId())
                json['coardinates']['latitude'] = float(json['coardinates']['latitude'])
                json['coardinates']['longitude'] = float(json['coardinates']['longitude'])
                
                id = mongo.db.outlet_notification.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except DuplicateKeyError:
            return {'error':{"message":["Outlet notification exist."]}},400
           

             