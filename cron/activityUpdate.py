#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId
import numpy as np

import Lib.log
log = Lib.log.getLogger(__name__)


class Outlet:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        
        self.city = self.getCity()   
        self.users = self.getUsers()
        #self.path = "/usr/local/var/www/pma/uploads/reports/"   
        #self.path = "/var/www/pmitest.redtons.com/uploads/reports/"   
        self.path = "/private/var/www/pma/uploads/reports/" 
        self.path = "/usr/share/www/liveApi/uploads/reports/"    
        
    def getCity(self):
        result = self.db.city.find()
        city = {}
        for row in result:
            city[str(row['_id'])] = row['name']
        return city   
    
    def getUsers(self):
        result = self.db.users.find()
        city = {}
        for row in result:
            city[str(row['_id'])] = {'name':row['name'],'code':row['code'],'parent':row['parent_id']}
        return city  
    
            
    def getUser(self,id):
        result = self.db.users.find_one({'_id':id})
        user = {}
        user['name'] = ''
        user['code'] = ''
        if result:
            user['name'] = result['name']
            user['code'] = result['code']
        

        result = self.db.users.find_one({'_id':result['parent_id']})
        supervisor = {}
        if result:
            supervisor['name'] = result['name']
            supervisor['code'] = result['code']
            
        return user,supervisor

    
    def getProductivityReport(self):
        
        try:
        
            count = 0
           
           
            query = {}
            #query['date'] = {'$gte': startDate, '$lt': endDate}
            #query['user_id']  = {"$in":user_ids}
            
          
            result = self.db.miform.find(query,{'activity_id':1,'offer_brand':1,'age':1}).limit(5)
            
            
            miLists = []
            for row in result:
                #row['activity_id'] = str(row['activity_id'])
                #row['offer_brand'] = str(row['offer_brand'])
                miLists.append(row)
             
            df = pd.DataFrame(miLists)   
            # Offered Brand table function
           
            data = {}
            ages = {}
            try:
                grouped = df.groupby(['activity_id','offer_brand'])
                offerBrandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                
                print(offerBrandTable)
                
                offerBrandTable = offerBrandTable.to_dict('index')
                
                
                grouped = df.groupby(['activity_id','age'])
                ageTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                print(ageTable)
                
                ageTable = ageTable.to_dict('index')
                
                
                
                
                age_total = 0
                
                for activity_id,age in ageTable:
                    
                    #print(age)
                    value = ageTable[(activity_id,age)]['_id']
                    
                    temp = {'18-24':0,'25-29':0,'30-34':0,'35-44':0,'>44':0}
                    if activity_id in ages:
                        temp = ages[activity_id]
                        
                    key = int(age)
                    
                    if key in range(18,24):
                        temp['18-24'] = temp['18-24']+value
                    elif key in range(25,29):
                        temp['25-29'] = temp['25-29']+value
                    elif key in range(30,34):
                        temp['30-34'] = temp['30-34']+value
                    elif key in range(35,44):
                        temp['35-44'] = temp['35-44']+value
                    else:
                        temp['>44'] = temp['>44']+value
                   
                    if activity_id in ages:
                        ages[activity_id].append(temp)
                    else:
                        ages[activity_id] = [temp]
                        
                #print(ages)
                
                #return offerBrandTable
                
                for activity_id,offer_brand in offerBrandTable:
                    value = offerBrandTable[(activity_id,offer_brand)]['_id']
                    
                    if activity_id in data:
                        data[activity_id].append({'id':offer_brand,'value':value})
                    else:
                        data[activity_id] = [{'id':offer_brand,'value':value}]
                
                #print(data)
                for key in data.keys():
                    row = data[key]
                    temp = {}
                    
                    for r in row:
                        temp[str(r['id'])] =  r['value']
                    
                    age = ages[key][0]
                    
                    self.db.today_outlet.update_one({'_id':key},{"$set":{'offer_brand':temp,'age_split':age}})
                    
                    
                   
                    
                    #data[row['date']] = row
                #print(brand_name)
               
            except Exception as e:
                print("Grouping Error: "+str(e))
           
        
        except Exception as e:
            print(e)
     
    def mipReport(self):
        try:
            
            report = self.getProductivityReport()
            
            #self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            #self.dateInput = datetime.strptime("2019-12-14","%Y-%m-%d")
            date = "2019-12-14"
            #print(date)
            self.dateInput = date
            dateStr = str(date).replace(" 00:00:00", "")
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            #aggr.append({"$match":{"date":self.dateInput}})
            aggr.append({"$sort" : { "date" : 1, "outlet_id": 1,"city_id":1 } })
            aggr.append({ "$limit" : 3 })
            #result = self.db.outlet_activity.aggregate(aggr)
        
            result = self.db.miform.aggregate(aggr)
            
            for row in result:
                key = (str(row['activity_id']),str(row['offer_brand']))
                if  key in report:
                    print(report['key'])
           
                
        except Exception as e:
            print("Error : "+ str(e) + "\n") 
            
    
 
 
o = Outlet()
o.getProductivityReport()



#o.mipReport()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")






