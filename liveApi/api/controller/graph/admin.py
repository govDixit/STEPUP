from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData,getCurrentUserId,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from api.lib.graphLib import graphLib


@apiV1.resource('/graph/admin/<int:id>')
class GraphAdmin(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'filter1': {'type': 'string','required': True,'empty': True},
                              'filter2': {'type': 'string','required': True,'empty': True},
                              'filter3': {'type': 'string','required': True,'empty': True}}
        
    def get(self,id):
        
        if id == 1:
            return self.getAgeSplit(),200
        elif id == 2:
            return self.getProductivity(),200
        elif id == 3:
            return self.getCompetitionSplit(),200
        else:
            return {'error':{"message":"Something Wrong"}},400
        
        
    def post(self,id):
        
        v = Validator(self.create_fields,allow_unknown=False)
        json = request.get_json()
        
        if v.validate(json):
            
            if id == 1:
                return self.getAgeSplit(),200
            elif id == 2:
                return self.getProductivity(),200
            elif id == 3:
                return self.getCompetitionSplit(),200
            else:
                return {'error':{"message":"Something Wrong"}},400
            
        else:
            return {'error':{"message":"Something Wrong"}},400 
            
        
        
        
    
    def getAgeSplit(self):
        
        try:
            
            gg = graphLib()
            month = gg.getMonthIPMStatics()
            week = gg.getWeekIPMStatics()
            today = gg.getTodayIPMStatics()
            
            #print(month)
        
            data = {"graph":"age_split",
                      "title":"Age Split Report",
                      "month":{"total":month['age']['total'],"type":"pie","label":month['age']['label'],"value":month['age']['value']},
                      "week":{"total":week['age']['total'],"type":"pie","label":week['age']['label'],"value":week['age']['value']},
                      "today":{"total":today['age']['total'],"type":"pie","label":today['age']['label'],"value":today['age']['value']},
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
            gg = graphLib()
            month = gg.getMonthIPMStatics()
            week = gg.getWeekIPMStatics()
            today = gg.getTodayIPMStatics()
            
            data = {"graph":"productivity",
                      "title":"Productivity Report",
                      "month":{"total":month['offerBrand']['total'],"type":"vbar","label":month['offerBrand']['label'],"value":month['offerBrand']['value']},
                      "week":{"total":week['offerBrand']['total'],"type":"vbar","label":week['offerBrand']['label'],"value":week['offerBrand']['value']},
                      "today":{"total":today['offerBrand']['total'],"type":"vbar","label":today['offerBrand']['label'],"value":today['offerBrand']['value']},
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
            gg = graphLib()
            month = gg.getMonthIPMStatics()
            week = gg.getWeekIPMStatics()
            today = gg.getTodayIPMStatics()
            
            data = {"graph":"competition",
                      "title":"Competition Split",
                      "month":{"total":month['brand']['total'],"type":"hbar","label":month['brand']['label'],"value":month['brand']['value']},
                      "week":{"total":week['brand']['total'],"type":"hbar","label":week['brand']['label'],"value":week['brand']['value']},
                      "today":{"total":today['brand']['total'],"type":"hbar","label":today['brand']['label'],"value":today['brand']['value']},
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
        
        
       
        
        
    
