from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData,getCurrentUserId,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from api.lib.graphLib import graphLib


@apiV1.resource('/graph/supervisor/<int:id>')
class GraphSupervisor(Resource):
    decorators = [check_permissions]
        
    def get(self,id):
        
        if id == 1:
            return self.getWorkingDays(),200
        elif id == 2:
            return self.getWorkingHours(),200
        elif id == 3:
            return self.getProductivity(),200
        else:
            return {'error':{"message":"Something Wrong"}},400
        
        
    
    def getWorkingDays(self):
        
        try:
            gg = graphLib()
            monthWorkingDays = gg.getMonthWorkingDays()
            weekWorkingDays = gg.getWeekWorkingDays()
            todayWorkingDays = gg.getTodayWorkingDays()
            
            data = {"graph":"working_days",
                      "title":"Working Days",
                      "month":{"total":int(monthWorkingDays['total']),"type":"hbar","label":monthWorkingDays['label'],"value":monthWorkingDays['value']},
                      "week":{"total":int(weekWorkingDays['total']),"type":"hbar","label":weekWorkingDays['label'],"value":weekWorkingDays['value']},
                      "today":{"total":int(todayWorkingDays['total']),"type":"hbar","label":todayWorkingDays['label'],"value":todayWorkingDays['value']}
                    }
            
            return data
        except:
            data = {"graph":"working_days",
                      "title":"Working Days",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
        
    def getWorkingHours(self):
        
        try:
            gg = graphLib()
            monthWorkingHours = gg.getMonthWorkingHours()
            weekWorkingHours = gg.getWeekWorkingHours()
            todayWorkingHours = gg.getTodayWorkingHours()
            
            data = {"graph":"working_hours",
                      "title":"Working Hours",
                      "month":{"total":int(monthWorkingHours['total']),"type":"hbar","label":monthWorkingHours['label'],"value":monthWorkingHours['value']},
                      "week":{"total":int(weekWorkingHours['total']),"type":"hbar","label":weekWorkingHours['label'],"value":weekWorkingHours['value']},
                      "today":{"total":int(todayWorkingHours['total']),"type":"hbar","label":todayWorkingHours['label'],"value":todayWorkingHours['value']}
                     }
                
            return data
        except:
            data = {"graph":"working_hours",
                      "title":"Working Hours",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                    }
            
            return data
        
    def getProductivity(self):
        
        try:
            gg = graphLib()
            monthProducitivity = gg.getMonthProductivityReport()
            weekProducitivity = gg.getWeekProductivityReport()
            todayProducitivity = gg.getTodayProductivityReport()
            
            data = {"graph":"productivity",
                      "title":"Productivity Report",
                      "month":{"total":int(monthProducitivity['total']),"type":"hbar","label":monthProducitivity['label'],"value":monthProducitivity['value']},
                      "week":{"total":int(weekProducitivity['total']),"type":"hbar","label":weekProducitivity['label'],"value":weekProducitivity['value']},
                      "today":{"total":int(todayProducitivity['total']),"type":"hbar","label":todayProducitivity['label'],"value":todayProducitivity['value']}
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
        
        
       
        
        
    
