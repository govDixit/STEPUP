from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getRow, requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json


@apiV1.resource('/statics/fwp')
class FwpStatics(Resource):
    
    def get(self):
        graph = []
        
        graph1 = {"graph":"working_days",
                  "title":"Working Days",
                  "month":{"total":345,"type":"hbar","label":['6th', '5th', '4th', '3rd', '2nd', '1st'],"value":[20, 22, 33, 44, 55, 40]},
                  "week":{"total":345,"type":"hbar","label":['6th', '5th', '4th', '3rd', '2nd', '1st'],"value":[20, 22, 33, 44, 55, 40]}
                 }
        
        graph2 = {"graph":"working_hours",
                  "title":"Working Hours",
                  "month":{"total":345,"type":"vbar","label":['Jan','Feb','Mar','Apr','May','June'],"value":[20,22,33,44,55,40]},
                  "week":{"total":345,"type":"vbar","label":['Jan','Feb','Mar','Apr','May','June'],"value":[20,22,33,44,55,40]}
                 }
        
        graph3 = {"graph":"ecc",
                  "title":"ECC",
                  "month":{"total":345,"type":"pie","label":['Jan','Feb','Mar','Apr','May','June'],"value":[20,22,33,44,55,40]},
                  "week":{"total":345,"type":"pie","label":['Jan','Feb','Mar','Apr','May','June'],"value":[20,22,33,44,55,40]}
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
                  "month":{"total":345,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[20, 22, 33, 44]},
                  "week":{"total":345,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[20, 22, 33, 44]},
                  "today":{"total":345,"type":"pie","label":['18-24', '25-34', '35-44', 'Other'],"value":[20, 22, 33, 44]}
                 }
        
        graph2 = {"graph":"productivity",
                  "title":"Productivity Report",
                  "month":{"total":345,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[20,22,33,44,55,40,45,46,33]},
                  "week":{"total":345,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[20,22,33,44,55,40,45,46,33]},
                  "today":{"total":345,"type":"vbar","label":['Red','Gold Advance','Gold','Fuse Beyond','Fine Touch','Clove Mix','Filter Black','Advance Compact','Beyond Compact'],"value":[20,22,33,44,55,40,45,46,33]},
                 }
        
        graph3 = {"graph":"competition",
                  "title":"Competition Split",
                  "month":{"total":345,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[20,22,33,44,55,40]},
                  "week":{"total":345,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[20,22,33,44,55,40]},
                  "today":{"total":345,"type":"hbar","label":['Gold Flake KS','Gold Flake RF','Classic','Benson & Hdeges','Marlboro','Other'],"value":[20,22,33,44,55,40]},
                 }
        
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200
    
    
@apiV1.resource('/statics/supervisor')
class SupervisorStatics(Resource):
    
    def get(self):
        graph = []
        
        graph1 = {"graph":"working_days",
                  "title":"Working Days",
                  "month":{"total":345,"type":"hbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                  "week":{"total":345,"type":"hbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                  "today":{"total":345,"type":"hbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                 }
        
        graph2 = {"graph":"avg_login",
                  "title":"Average Login",
                  "month":{"total":345,"type":"vbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                  "week":{"total":345,"type":"vbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                  "today":{"total":345,"type":"vbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                 }
        
        graph3 = {"graph":"productivity",
                  "title":"Productivity Report",
                  "month":{"total":345,"type":"vbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                  "week":{"total":345,"type":"vbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                  "today":{"total":345,"type":"vbar","label":['FWP1', 'FWP2', 'FWP3', 'FWP4', 'FWP5', 'FWP6', 'FWP7','FWP8','FWP9','FWP10'],"value":[20, 22, 33, 44, 55, 40, 55,40,43,35]},
                 }
        
        graph.append(graph1)
        graph.append(graph2)
        graph.append(graph3)
        return graph,200
    

