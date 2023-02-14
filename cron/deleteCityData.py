#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId
import calendar
import copy 


import os



import Lib.log
log = Lib.log.getLogger(__name__)

def getId(id):
    try:
        return ObjectId(id)
    except:
        return False

class UpdateDb:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        
        #self.city = self.getCity() 
        #self.dates = self.getDays()  
    def getCity(self):
        result = self.db.city.find({'status':3})
        city = {}
        for row in result:
            city[str(row['_id'])] = row['name']
        return city
    
    
    def deleteMiForm(self):
        cities = self.getCity()    
        #print(cities)
        
        for city_id in cities:
            print(city_id)
            result = self.db.miform.find({'city_id':ObjectId(str(city_id))})
            
            for row in result:
                file = "/usr/share/www/liveApi/"+row['signature']
                
                if os.path.exists(file):
                    os.remove(file)
                    print("Done "+file+"\n")
                else:
                    print("Can not delete the file as it doesn't exists\n")
                
            self.db.miform.delete_many({'city_id':ObjectId(str(city_id))})
            
            #self.db.users.delete_many({'city_id':ObjectId(str(city_id))})
            
            """self.db.today_outlet.delete_many({'city_id':ObjectId(str(city_id))})
            self.db.outlet_activity.delete_many({'city_id':ObjectId(str(city_id))})
            self.db.outlet.delete_many({'city_id':ObjectId(str(city_id))})"""
            
            
    def deleteOutlet(self):
        cities = self.getCity()    
        #print(cities)
        
        for city_id in cities:
            print(city_id)
            """result = self.db.outlet.find({'city_id':ObjectId(str(city_id))})
            
            for row in result:
                self.db.today_outlet.delete_many({'outlet_id': row['_id'] })
                self.db.outlet_activity.delete_many({'outlet_id': row['_id'] })"""
                
            self.db.outlet.delete_many({'city_id':ObjectId(str(city_id))})
    
    
            
    def deleteUser(self):
        cities = self.getCity()    
        #print(cities)
        
        for city_id in cities:
            print(city_id)
            result = self.db.users.find({'city_id':ObjectId(str(city_id))})
            
            for row in result:
                self.db.attendance.delete_many({'user_id': row['_id'] })
                
            self.db.users.delete_many({'city_id':ObjectId(str(city_id))})
            
          
       
                
o = UpdateDb()

#o.deleteMiForm()
#o.deleteOutlet()

o.deleteUser()

#o.userCityId()
#o.outletCityId()


#print(areas)

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







