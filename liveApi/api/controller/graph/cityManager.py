from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData,getCurrentUserId,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from api.lib.graphLib import graphLib


@apiV1.resource('/graph/citymanager/<int:id>')
class GraphCityManager(Resource):
    decorators = [check_permissions]
    
    def get(self,id):
        
        if id == 1:
            return self.getAgeSplit(),200
        elif id == 2:
            return self.getProductivity(),200
        elif id == 3:
            return self.getCompetitionSplit(),200
        else:
            return {'error':{"message":"Something Wrong"}},400
        
        
    
    def getAgeSplit(self):
        
        try:
            
            data = {"graph":"age_split",
                      "title":"Age Split Report",
                      "month":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                      "week":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                      "today":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                     }
            
            return data
        except:
            data = {"graph":"age_split",
                      "title":"Age Split Report",
                      "month":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                      "week":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                      "today":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                     }
            
            return data
        
        
    
    def getProductivity(self):
        
        try:
            data = {"graph":"productivity",
                      "title":"Productivity Report",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
                
            return data
        except:
            data = {"graph":"productivity",
                      "title":"Productivity Report",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
    
    def getCompetitionSplit(self):
        try:
            data = {"graph":"competition",
                      "title":"Productivity Report",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
                
            return data
        except:
            data = {"graph":"competition",
                      "title":"Competition Split",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
        
       
        
        
    
