from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json


@apiV1.resource('/products')
class PropuctList(Resource):
    
    def get(self):
        result = mongo.db.products.find_one({'_id':getId('5d981ae25581b73e99d6b5c7')})
        temp = []
        for row in result['variant']:
            temp.append(getRow(row))
            
        return temp,200
    
    

