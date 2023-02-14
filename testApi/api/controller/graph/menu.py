from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData,getCurrentUserId,getCurrentUser
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from api.lib.graphLib import graphLib


@apiV1.resource('/graph/menu')
class GraphMenu(Resource):
    
    def get(self):
        
        self.user = getCurrentUser() 
        
        data = []
        
        if self.user['role'] == 1:
            data.append({"title":"Working Days","uri":"graph/fwp/1"})
            data.append({"title":"Working Hours","uri":"graph/fwp/2"})
            data.append({"title":"ECC","uri":"graph/fwp/3"})
            
        elif self.user['role'] == 2:
            data.append({"title":"Working Days","uri":"graph/supervisor/1"})
            data.append({"title":"Working Hours","uri":"graph/supervisor/2"})
            data.append({"title":"Productivity Report","uri":"graph/supervisor/3"})
            
        
        elif self.user['role'] == 3:
            data.append({"title":"Age Split Report","uri":"graph/citymanager/1"})
            data.append({"title":"Productivity Report","uri":"graph/citymanager/2"})
            data.append({"title":"Competition Split","uri":"graph/citymanager/3"})
            
        elif self.user['role'] > 3:
            data.append({"title":"Age Split Report","uri":"graph/admin/1"})
            data.append({"title":"Productivity Report","uri":"graph/admin/2"})
            data.append({"title":"Competition Split","uri":"graph/admin/3"})
            
            
        return data,200
        


