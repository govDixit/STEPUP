from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData,getCurrentUserId,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from api.lib.graphLib import graphLib


@apiV1.resource('/graph/fwp/<int:id>')
class GraphFwp(Resource):
    decorators = [check_permissions]
    
    def get(self,id):
        
        if id == 1:
            return self.getWorkingDays(),200
        elif id == 2:
            return self.getWorkingHours(),200
        elif id == 3:
            return self.getECC(),200
        else:
            return {'error':{"message":"Something Wrong"}},400
        
        
    
    def getWorkingDays(self):
        
        try:
            gg = graphLib()
            monthWorkingDays = gg.getMonthWorkingDays(True)
            weekWorkingDays = gg.getWeekWorkingDays(True)
            
            data = {"graph":"working_days",
                      "title":"Working Days",
                      "month":{"total":int(monthWorkingDays['total']),"type":"hbar","label":monthWorkingDays['label'],"value":monthWorkingDays['value']},
                      "week":{"total":int(weekWorkingDays['total']),"type":"hbar","label":weekWorkingDays['label'],"value":weekWorkingDays['value']},
                    }
            
            return data
        except:
            data = {"graph":"working_days",
                      "title":"Working Days",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
        
    def getWorkingHours(self):
        
        try:
            gg = graphLib()
            monthWorkingHours = gg.getMonthWorkingHours(True)
            weekWorkingHours = gg.getWeekWorkingHours(True)
            
            data = {"graph":"working_hours",
                      "title":"Working Hours",
                      "month":{"total":int(monthWorkingHours['total']),"type":"hbar","label":monthWorkingHours['label'],"value":monthWorkingHours['value']},
                      "week":{"total":int(weekWorkingHours['total']),"type":"hbar","label":weekWorkingHours['label'],"value":weekWorkingHours['value']},
                     }
                
            return data
        except:
            data = {"graph":"working_hours",
                      "title":"Working Hours",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
    def getECC(self):
        
        try:
            gg = graphLib()
            monthEcc = gg.getMonthECC()
            weekEcc = gg.getWeekECC()
            
            data = {"graph":"ecc",
                      "title":"ECC",
                      "month":{"total":int(monthEcc['total']),"type":"hbar","label":monthEcc['label'],"value":monthEcc['value']},
                      "week":{"total":int(weekEcc['total']),"type":"hbar","label":weekEcc['label'],"value":weekEcc['value']}
                     }
                
            return data
        except:
            data = {"graph":"ecc",
                      "title":"ECC",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
        
       
        
        
    
