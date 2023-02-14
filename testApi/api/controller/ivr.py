from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json




@apiV1.resource('/ivr/<id>')
class Ivr(Resource):
    
    
    #data = {"customer_missed_number":"","agent_missed_number":"","dispnumber":"+917428096123","extension":"None","callid":"4cd60251-1a04-4345-b9a6-5306939c30ea","call_duration":"0","destination":"Missed Call","caller_id":"+919999097324","end_time":"2020-01-22 13:38:52.218728+05:30","action":"8","timezone":"Asia\/Kolkata","resource_url":"","hangup_cause":"900","type":"missed call","start_time":"2020-01-22 13:38:52.218728+05:30","call_type":"incoming"}    
    def get(self,id):
        print(id)
            
        
    
    