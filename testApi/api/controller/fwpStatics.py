from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData,getCurrentUserId
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from api.lib.graphLib import graphLib


@apiV1.resource('/statics/fwp')
class FwpStatics(Resource):
    
    def get(self):
        
        gg = graphLib()
        
       
        monthEcc = gg.getMonthECC()
        weekEcc = gg.getWeekECC()
        
        monthWorkingDays = gg.getMonthWorkingDays(True)
        weekWorkingDays = gg.getWeekWorkingDays(True)
        
        
        monthWorkingHours = gg.getMonthWorkingHours(True)
        weekWorkingHours = gg.getWeekWorkingHours(True)
        
      
        
        graph = []
        
        graph1 = {"graph":"working_days",
                  "title":"Working Days",
                  "month":{"total":int(monthWorkingDays['total']),"type":"hbar","label":monthWorkingDays['label'],"value":monthWorkingDays['value']},
                  "week":{"total":int(weekWorkingDays['total']),"type":"hbar","label":weekWorkingDays['label'],"value":weekWorkingDays['value']},
                }
                  
       
        
        graph2 = {"graph":"working_hours",
                  "title":"Working Hours",
                  "month":{"total":int(monthWorkingHours['total']),"type":"hbar","label":monthWorkingHours['label'],"value":monthWorkingHours['value']},
                  "week":{"total":int(weekWorkingHours['total']),"type":"hbar","label":weekWorkingHours['label'],"value":weekWorkingHours['value']},
                 }
        
        graph3 = {"graph":"ecc",
                  "title":"ECC",
                  "month":{"total":int(monthEcc['total']),"type":"hbar","label":monthEcc['label'],"value":monthEcc['value']},
                  "week":{"total":int(weekEcc['total']),"type":"hbar","label":weekEcc['label'],"value":weekEcc['value']}
                 }
        
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200
    
    
    

    
@apiV1.resource('/statics/supervisor')
class SupervisorStatics(Resource):
    
    def get(self):
        
        gg = graphLib()
        monthProducitivity = gg.getMonthProductivityReport()
        weekProducitivity = gg.getWeekProductivityReport()
        todayProducitivity = gg.getTodayProductivityReport()
        
        monthWorkingDays = gg.getMonthWorkingDays()
        weekWorkingDays = gg.getWeekWorkingDays()
        todayWorkingDays = gg.getTodayWorkingDays()
        
        
        monthWorkingHours = gg.getMonthWorkingHours()
        weekWorkingHours = gg.getWeekWorkingHours()
        todayWorkingHours = gg.getTodayWorkingHours()
        
        
        graph = []
        
        graph1 = {"graph":"working_days",
                  "title":"Working Days",
                  "month":{"total":int(monthWorkingDays['total']),"type":"hbar","label":monthWorkingDays['label'],"value":monthWorkingDays['value']},
                  "week":{"total":int(weekWorkingDays['total']),"type":"hbar","label":weekWorkingDays['label'],"value":weekWorkingDays['value']},
                  "today":{"total":int(todayWorkingDays['total']),"type":"hbar","label":todayWorkingDays['label'],"value":todayWorkingDays['value']}
                 }
        
        
        graph2 = {"graph":"working_hours",
                  "title":"Working Hours",
                  "month":{"total":int(monthWorkingHours['total']),"type":"hbar","label":monthWorkingHours['label'],"value":monthWorkingHours['value']},
                  "week":{"total":int(weekWorkingHours['total']),"type":"hbar","label":weekWorkingHours['label'],"value":weekWorkingHours['value']},
                  "today":{"total":int(todayWorkingHours['total']),"type":"hbar","label":todayWorkingHours['label'],"value":todayWorkingHours['value']}
                 }
        
        
        """graph2 = {"graph":"avg_login",
                  "title":"Average Login",
                  "month":{"total":0,"type":"hbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[0, 0, 0, 0, 0, 0, 0,0,0,0]},
                  "week":{"total":0,"type":"hbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[0, 0, 0, 0, 0, 0, 0,0,0,0]},
                  "today":{"total":0,"type":"hbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[0, 0, 0, 0, 0, 0, 0,0,0,0]},
                 }"""
        
        graph3 = {"graph":"productivity",
                  "title":"Productivity Report",
                  "month":{"total":int(monthProducitivity['total']),"type":"hbar","label":monthProducitivity['label'],"value":monthProducitivity['value']},
                  "week":{"total":int(weekProducitivity['total']),"type":"hbar","label":weekProducitivity['label'],"value":weekProducitivity['value']},
                  "today":{"total":int(todayProducitivity['total']),"type":"hbar","label":todayProducitivity['label'],"value":todayProducitivity['value']}
                 }
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200
    
        
    
@apiV1.resource('/statics/citymanager')
class CityManagerStatics(Resource):
    
    def get(self):
        graph = []
        
        graph1 = {"graph":"age_split",
                  "title":"Age Split Report",
                  "month":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                  "week":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                  "today":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                 }
        
        graph2 = {"graph":"productivity",
                  "title":"Productivity Report",
                  "month":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                  "week":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                  "today":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                 }
        
        graph3 = {"graph":"competition",
                  "title":"Competition Split",
                  "month":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                  "week":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                  "today":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                 }
        
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200
    

    
    
    
@apiV1.resource('/statics/ipm')
class IPMStatics(Resource):
    
    def __init__(self):
        self.create_fields = {'filter1': {'type': 'string','required': True,'empty': True},
                              'filter2': {'type': 'string','required': True,'empty': True},
                              'filter3': {'type': 'string','required': True,'empty': True}}
        
        
        
    def get(self):
        graph = []
        
        
        gg = graphLib()
        month = gg.getMonthIPMStatics()
        
        
        #print(month)
        
        #week = gg.getWeekIPMStatics()
        #today = gg.getTodayIPMStatics()
        
        
        
        
        graph1 = {"graph":"age_split",
                  "title":"Age Split Report",
                  "month":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                  "week":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                  "today":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                 }
        
        graph2 = {"graph":"productivity",
                  "title":"Productivity Report",
                  "month":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                  "week":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                  "today":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                 }
        
        graph3 = {"graph":"competition",
                  "title":"Competition Split",
                  "month":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                  "week":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                  "today":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                 }
        
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200
    
    def post(self):
        """graph = []
        graph11 = {"graph":"age_split",
                  "title":"Age Split Report",
                  "month":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                  "week":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                  "today":{"total":0,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[0, 0, 0, 0]},
                 }
        
        graph12 = {"graph":"productivity",
                  "title":"Productivity Report",
                  "month":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                  "week":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                  "today":{"total":0,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[0,0,0,0,0,0,0,0,0]},
                 }
        
        graph13 = {"graph":"competition",
                  "title":"Competition Split",
                  "month":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                  "week":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                  "today":{"total":0,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[0,0,0,0,0,0]},
                 }
        
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200"""
    
    
        v = Validator(self.create_fields,allow_unknown=False)
        json = request.get_json()
        if v.validate(json):
            graph = []
            
            
            gg = graphLib()
            month = gg.getMonthIPMStatics()
            week = gg.getWeekIPMStatics()
            today = gg.getTodayIPMStatics()
            
            #print(month)
        
            graph1 = {"graph":"age_split",
                      "title":"Age Split Report",
                      "month":{"total":month['age']['total'],"type":"pie","label":month['age']['label'],"value":month['age']['value']},
                      "week":{"total":week['age']['total'],"type":"pie","label":week['age']['label'],"value":week['age']['value']},
                      "today":{"total":today['age']['total'],"type":"pie","label":today['age']['label'],"value":today['age']['value']},
                      }
        
            graph2 = {"graph":"productivity",
                      "title":"Productivity Report",
                      "month":{"total":month['offerBrand']['total'],"type":"vbar","label":month['offerBrand']['label'],"value":month['offerBrand']['value']},
                      "week":{"total":week['offerBrand']['total'],"type":"vbar","label":week['offerBrand']['label'],"value":week['offerBrand']['value']},
                      "today":{"total":today['offerBrand']['total'],"type":"vbar","label":today['offerBrand']['label'],"value":today['offerBrand']['value']},
                     }
            
            graph3 = {"graph":"competition",
                      "title":"Competition Split",
                      "month":{"total":month['brand']['total'],"type":"hbar","label":month['brand']['label'],"value":month['brand']['value']},
                      "week":{"total":week['brand']['total'],"type":"hbar","label":week['brand']['label'],"value":week['brand']['value']},
                      "today":{"total":today['brand']['total'],"type":"hbar","label":today['brand']['label'],"value":today['brand']['value']},
                     }
            
            
            graph.append(graph1)
            graph.append(graph2)
            graph.append(graph3)
            return graph,200
        
        else:
            
            graph = []
            
            graph1 = {"graph":"age_split",
                  "title":"Age Split Report",
                  "month":{"total":0,"type":"hbar","label":['18-24'],"value":[10]},
                  "week":{"total":0,"type":"hbar","label":[],"value":[]},
                  "today":{"total":0,"type":"hbar","label":[],"value":[]},
                 }
        
            graph2 = {"graph":"productivity",
                      "title":"Productivity Report",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                     }
            
            graph3 = {"graph":"competition",
                      "title":"Competition Split",
                      "month":{"total":0,"type":"hbar","label":[],"value":[]},
                      "week":{"total":0,"type":"hbar","label":[],"value":[]},
                      "today":{"total":0,"type":"hbar","label":[],"value":[]},
                     }
            
            
            graph.append(graph1)
            graph.append(graph2)
            graph.append(graph3)
            return graph,200
        
        
        
        
        
        

