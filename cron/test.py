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
import numpy as np


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
        
        
    def test(self):
        #print(query)    
        productResults = self.db.products.find()
        products = {}
        for row in productResults:
            products[str(row['_id'])] = row['name']
                
        result = self.db.miform.find({},{'brands':1,'offer_brand':1,'user_id':1,'gender':1,'age':1,'area':1})
        
        total = result.count()
        achievement = {'cc':total,'ecc':total}
        
        
        df = pd.DataFrame(list(result))
        #print(df) 
        
        # Brand table function
        brand_label = []
        brand_value = []
        try:
            grouped = df.groupby('brands')
            brandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
            
            print(brandTable)
            brandTable = brandTable.to_dict('index')
            
            for key in brandTable.keys():
                value = brandTable[key]['_id']
                brand_label.append(products[str(key)])
                brand_value.append(value)
        except:
            pass
        
        print(brand_label)
        print(brand_value)    
    
o = UpdateDb()
o.test()


#print(areas)

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







