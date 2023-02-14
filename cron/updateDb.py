#!/usr/local/bin/python3
exit()
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId
import calendar
import copy 



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
        result = self.db.city.find()
        city = {}
        for row in result:
            city[str(row['_id'])] = row['name']
        return city   
            
    def getArea(self):
        result = self.db.miform.aggregate([ {"$group" :{ "_id": { "city_id":"$city_id","area": "$area" } } } ])
        self.areas1 = {}
        
        
        if result:
            #print(result)
            for row in result:
                
                row = row['_id']
                #print(row)
                
                if str(row['city_id']) in self.areas1:
                    self.areas1[str(row['city_id'])].append(row['area'])
                else:
                    self.areas1[str(row['city_id'])] = []
                    self.areas1[str(row['city_id'])].append(row['area'])
            
        return self.areas1


    def updateCityArea(self,data):
        for k in data.keys():
            row = data[k]
            print({'_id':ObjectId(k)},{"$set":{'areas':row}})
            self.db.city.update({'_id':ObjectId(k)},{"$set":{'areas':row}})
            
            
    def userCityId(self):
        rs = self.db.user.find()
        for row in rs:
            #print(row)
            self.db.user.update_one( {"_id":row['_id']}, {"$set": {"city_id":getId(str(row['city_id']))}})
        print("Done user city")        
                
    def outletCityId(self):
        rs = self.db.outlet.find()
        for row in rs:
            #print(row)
            self.db.outlet.update_one( {"_id":row['_id']}, {"$set": {"city_id":getId(str(row['city_id']))}})
        print("Done outlet city")       
    
    
        
    def updateFormBrand(self):
        result = self.db.miform.find()
        
        for row in result:
            self.db.miform.update_one({'_id':row['_id']},{"$set":{'brands':ObjectId(str(row['brands']))}})
            
       
                
o = UpdateDb()
o.updateFormBrand()

#o.userCityId()
#o.outletCityId()


#print(areas)

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







