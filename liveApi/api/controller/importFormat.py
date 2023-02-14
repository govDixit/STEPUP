from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from flask_jwt_extended import get_jwt_identity
from datetime import date,datetime



@apiV1.resource('/format/<filename>')
class ImportFormat(Resource):
    
    def get(self,filename):
        try:
            path = "../download/"+filename
            return send_file(path, as_attachment=True)
        except:
            return {'error':{"message":"Something Wrong."}},400
    
    
  
