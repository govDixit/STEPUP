#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
from bson import ObjectId
import calendar
import copy 
import xlsxwriter
from collections import defaultdict
from xlsxwriter.utility import xl_rowcol_to_cell,xl_col_to_name


import Lib.log
log = Lib.log.getLogger(__name__)


class Attendance:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        
    
    
    def workingHours(self):
        
        try:
            yesterday = (date.today() - timedelta(days=1))
            date1  =  datetime.strptime(str(yesterday),"%Y-%m-%d")
            #print(date1)
            #exit()
            #$date1  =  datetime.strptime("2019-12-18","%Y-%m-%d")
            
            
            #print(date1)
            users = {}
            #result = self.db.outlet_activity.find({'date':date1})
            
            result = self.db.outlet_activity.find()
            
            for row in result:
                checkin_activity = row['checkin_activity']
                sec = self.calculateHours(checkin_activity)
                
                
                try:
                    self.dateInput = datetime.strptime(str(row['date'].date()),"%Y-%m-%d")
                    
                    myquery = {"user_id":row['fwp_id'],"date":self.dateInput}
                    newvalues = { "$set": {"duration": int(sec)} }
                    self.db.attendance.update_one(myquery, newvalues)
                    
                except Exception as e:
                    print(e)
                    #exit()
                
            ## update working hours in supervisor attendance
            sup_result = self.db.attendance.find({ 'supervisor_checkin_activity' : { "$exists": True, "$ne": None } });
            
            for row in sup_result:
                if 'supervisor_checkin_activity' in row:
                    checkin_activity = row['supervisor_checkin_activity']
                    sec = self.calculateHours(checkin_activity)
                
                    try:
                        self.dateInput = datetime.strptime(str(row['date'].date()),"%Y-%m-%d")
                        
                        myquery = {"user_id":row['user_id'],"date":self.dateInput}
                        newvalues = { "$set": {"duration": int(sec)} }
                        self.db.attendance.update_one(myquery, newvalues)
                        
                    except Exception as e:
                        print(e)
                else:
                    pass
        except Exception as e:
            print(e)
            
    
    def calculateHours(self,checkin_activity):
        try:
            sec = 0
            for row in checkin_activity:
                start = row['start']['date']
                end = row['end']['date']
                # ~ print(start,end) 
              
                if end != None:
                    diff = end - start
                    diff = diff.total_seconds()
                    sec = sec + diff
                else:
                    ## condition added by sagar
                    sec = 0
                    # ~ sec = 10*60*60
                    
            return sec
                
                
        except Exception as e:
            ## condition added by sagar
            sec = 0 
            # ~ sec = 10*60*60 
            
    """def workingHours(self):
        
        try:
            date1  =  datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            date1  =  datetime.strptime("2019-12-18","%Y-%m-%d")
            
            
            print(date1)
            users = {}
            result = self.db.outlet_activity.find({'date':date1})
            
            #result = self.db.outlet_activity.find()
            
            for row in result:
                checkin_activity = row['checkin_activity']
                
                for c in checkin_activity:
                    print(c['start']['date'],c['end']['date'])
                    end = c['end']['date']
                    if end != None:
                        try:
                            self.dateInput = datetime.strptime(str(row['date'].date()),"%Y-%m-%d")
                            checkout_date =  (end + timedelta(hours=12))
                            
                            myquery = {"outlet_id":row['outlet_id'],"date":self.dateInput,"checkin_activity.id":c['id']}
                            newvalues = {"$set": {"checkin_activity.$.end.date":checkout_date}}
                            self.db.today_outlet.update_one(myquery, newvalues)
                            self.db.outlet_activity.update_one(myquery, newvalues) 
                        except Exception as e:
                            print(e)
                            #exit()
                        
                
                #print(checkin_activity)
                #self.calculateHours(checkin_activity)
                
            
        except Exception as e:
            print(e)"""
            
    
    
    """def calculateErrorLevel(self):
        
        try:
            #date1  =  datetime.strptime(str(date.yesterday()),"%Y-%m-%d")
            
            #$date1  =  datetime.strptime("2019-12-18","%Y-%m-%d")
            
            
            #print(date1)
            users = {}
            result = self.db.notification.find()
            
            #result = self.db.outlet_activity.find()
            
            
            
            for row in result:
                self.dateInput = datetime.strptime(str(row['date'].date()),"%Y-%m-%d")
                myquery = {"user_id":row['user_id'],"date":self.dateInput}
                newvalues = { "$inc": {"error_level": int(1)} }
                self.db.attendance.update_one(myquery, newvalues)
               
        except Exception as e:
            print(e)  """         
            
                
o = Attendance()
o.workingHours()
#o.calculateErrorLevel()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







