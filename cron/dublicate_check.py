#!/usr/local/bin/python3
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId
import calendar
from pymongo import MongoClient

client = MongoClient('mongodb://pmi:Title321@localhost:27017/pmi_test')
db = client.pmi_test
            
def start():
    try:
      
        fromDate = "2020-10-06"
        fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d")
        toDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d") + timedelta(days=1)
       
        #result = db.miform.find({'date':{"$gte": fromDate1, "$lt": toDate1}})
        
        result = db.miform.find()
        
        r = list(result)
        df = pd.DataFrame(r)
        print(df)
      
        df1 = pd.DataFrame(r, columns = ['user_id','date']) 
        
        data = df1[df1.duplicated()]
        c = 0
        for row in data.index:
            #print(data['user_id'][row],row)
            r = df.iloc[row, 0:1]
            id = r['_id']
            print("Result :",r['_id'],c)
            c = c+1
            
            #db.miform.delete_one({'_id':id})
            
        #print(df[df.duplicated()])
  
        
           
    except Exception as e:
        print(e)
dateInput = datetime.strptime("2020-10-06 13:01:09", "%Y-%m-%d %H:%M:%S")
r = db.miform.find_one({'date':dateInput,'user_id':ObjectId('5f75e15e55dac7e22f7f8f42')}) 

if r:
    print("this is dublicate",r['_id'])
else:
    print("This is new",r)

#start()
#print("Start.....")
#o.activeOutletReport()
print("Completed.....")


















