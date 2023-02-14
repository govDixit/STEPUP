#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta

import calendar

import Lib.log
log = Lib.log.getLogger(__name__)


class Logs:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        
    
    def deleteBefore30Days(self):
        
        date1 = date.today() + timedelta(-30)
        self.dateInput = datetime.strptime(str(date1),"%Y-%m-%d")
       
        print(self.dateInput)
        result = self.db.logs.remove({'created_at':{'$lte' : self.dateInput}})
    
 
o = Logs()
o.deleteBefore30Days()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







