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



class Dashboard:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        self.roles = {1:'FWP',2:'SUPERVISOR',3:'CITY MANAGER',4:'IPM'}
        self.city = self.getCity() 
        
        #self.path = "/var/www/pma/uploads/reports/"   
        #self.path = "/var/www/pmitest.redtons.com/uploads/reports/"   
        self.path = "/usr/share/www/liveApi/uploads/reports/"   
        
       
        
    def getCity(self):
        result = self.db.city.find()
        city = {}
        city['False'] = 'No City'
        for row in result:
            city[str(row['_id'])] = row['name']
        return city   
            
    def getUser(self,city_id):
        result = self.db.users.find({'city_id':city_id})
        self.users = {}
        if result:
            for row in result:
                self.users[str(row['_id'])] = row
            
        return self.users


    def getDays(self,date1):
        try:
            self.columns = ['SR.NO','CITY','FWP','MIC','MIC / FWP']
            self.row = {}
            self.row['SR.NO'] = ''
            self.row['CITY'] = ''
            
            self.row['FWP'] = {'NAME':'FWP'}
            self.row['MIC'] = {'NAME':'MIC'}
            self.row['MIC / FWP'] = {'NAME':'MIC / FWP'}
            
            self.row['Date'] = {'Date':'Date'}
            self.row['Day'] = {'Day':'Day'}
            
            self.row['TOTAL'] = 0
           
           
            #print(date1)
            date1  =  datetime.strptime(str(date1.date()),"%Y-%m-%d")
            #print(date1)
            #date1  =  datetime.strptime(str("2019-10-01"),"%Y-%m-%d")
            
            
            startDate = date1.replace(day = 1)
            endDate = date1.replace(day = calendar.monthrange(date1.year, date1.month)[1])
            
            
            self.startDate = startDate
            self.endDate = endDate
            
            
            dates = []
            for n in range(int ((endDate - startDate).days)+1):
                d = startDate + timedelta(n)
                dates.append(d)
                self.columns.append(d.strftime("%d-%b"))
                
                self.row['Date'][d.strftime("%d-%b")] = True
                self.row['Day'][d.strftime("%d-%b")] = d.strftime("%a")
                
             
                self.row['FWP'][d.strftime("%d-%b")] = 0
                self.row['MIC'][d.strftime("%d-%b")] = 0
                self.row['MIC / FWP'][d.strftime("%d-%b")] = 0
               
                
            self.row['FWP']['TOTAL'] = 0
            self.row['MIC']['TOTAL'] = 0
            self.row['MIC / FWP']['TOTAL'] = 0
            
            return dates
        
        except Exception as e:
            print("Date Error : " + str(e))
        
    
    #for Cycle
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
        
        try:
           
            header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#000000','bg_color':'#768a94','border':1,'border_color':'#000000'})
            bottom_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#000000','bg_color':'#d8d8d8','border':7,'border_color':'#7fb7df'})
            
            
            divider_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#000000','bg_color':'#7f7f7f','border':7,'border_color':'#7fb7df'})
            wdivider_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#000000','bg_color':'#ffffff','border':0,'border_color':'#7fb7df'})
           
            mtd_format = workbook.add_format({'align':'center','bold': True, 'font_size':24,'font_color': '#000000','bg_color':'#538ed5','border':1,'border_color':'#000000'})
            
            
            city_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#000000','bg_color':'#b7dee8','border':7,'border_color':'#7fb7df'})
            cell_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#000000','bg_color':'#ffffff','border':7,'border_color':'#7fb7df'})
            
          
            
            c = 0   #Row
            rc = 0 #Row Column
           
            for r in self.row['Date']:
                worksheet.write(c,rc,r,header_format)
                rc += 1
            
            c += 1 
            rc = 0   
            for k in self.row['Day']:
                worksheet.write(c,rc,self.row['Day'][k],header_format)
                rc += 1
            
            
            #for MTD last column
            cell = xl_col_to_name((rc))
            cell1 = xl_col_to_name((rc-1))
            worksheet.merge_range(str(cell)+'1:'+str(cell)+'2','MTD',mtd_format)   
            
            #worksheet.merge_range('AG1:AG2','MTD',mtd_format)   
            
            srNo = 0
            startC = c + 2
           
            for k in data:
                rows = data[k]
                c += 1
               
                worksheet.write(c,0,k,city_format)
                worksheet.write(c,rc,k,city_format)
                worksheet.merge_range('B'+str(c+1)+':'+str(cell1)+str(c+1),'',wdivider_format)  
                
                
                c += 1
                self.__insertRow(worksheet,c,rows['FWP'],cell_format)
                
                
                c += 1
                self.__insertRow(worksheet,c,rows['MIC'],cell_format)
                c += 1
                self.__insertRow(worksheet,c,rows['MIC / FWP'],bottom_format)
                c += 1
                self.__insertRow(worksheet,c,[],divider_format)
                
                #for Last divider of City
                worksheet.merge_range('A'+str(c+1)+':'+str(cell)+str(c+1),'',divider_format)  
               
            
                worksheet.merge_range('A'+str(c+2)+':'+str(cell)+str(c+2),'',wdivider_format)  
                worksheet.merge_range('A'+str(c+3)+':'+str(cell)+str(c+3),'',wdivider_format)  
                
                
                c += 2
              
                
            return c+2
        except Exception as e:
            print("Error - Insert Worksheet : "+str(e))
            
        
    
    # For City            
    def __insertRow(self,worksheet,c,row,cell_format):   
        try:
           
            rc = 0
            #print(row)
            #exit()
            for k in row:
                
                if k == "NAME":
                    worksheet.write(c,rc,row[k],cell_format)
                else:
                    worksheet.write(c,rc,row[k],cell_format)
               
                if k == 'TOTAL':
                    cell = xl_col_to_name((rc-1))
                    worksheet.write(c,rc,"=SUM(B"+str(c+1)+":"+str(cell)+str(c+1)+")",cell_format)
                
                rc += 1
            #worksheet.write(c,0,srNo)
            return rc
        except Exception as e:
            print("Error - Insert Row : "+str(e))
        
        
        
      
    
    def report1(self,req):
        try:
            date = req['filter']['date']
            self.dates = self.getDays(date)  
            
            
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            aggr.append({"$match":{"date":{"$gte":self.startDate,"$lte":self.endDate} } })
            
            
            result = self.db.outlet_activity.aggregate(aggr)
            #result = self.db.today_outlet.aggregate(aggr)
            
            
            #self.cities = defaultdict(lambda: defaultdict(list))
            self.cycle = defaultdict(lambda: defaultdict(list))
            
            self.fwps = defaultdict(lambda: defaultdict(list))
            
            data = {}
            #data = []
            for row in result:
                #print(row)
                t = {}
                id = str(row['fwp_id'])
                
                city = self.city[str(row['outlet']['city_id'])]
                cycle = str(row['activity']).upper().strip()
                date_col = row['date'].strftime("%d-%b")
                
                if len(self.cycle[cycle][city]) > 0:
                    t = self.cycle[cycle][city]
                    #print(t)
                    if str(row['fwp_id']) not in self.fwps[date_col]:
                        
                        self.fwps[date_col][str(row['fwp_id'])] = 1
                        
                        if self.isAttandenceMark(row['fwp_id'],row['date']):
                            t['FWP'][date_col] = t['FWP'][date_col] + 1
                        
                    
                    #t['FWP'][date_col] = t['FWP'][date_col] + 1
                    t['MIC'][date_col] = t['MIC'][date_col] + self.getTotalForms(row['_id'])
                    
                    if t['FWP'][date_col]:
                        t['MIC / FWP'][date_col] = round(t['MIC'][date_col] / t['FWP'][date_col])
                   
                    self.cycle[cycle][city] = t
                else:
                    t = copy.deepcopy(self.row) 
                    t['CITY'] = city
                    t['CYCLE'] = cycle
                    
                    #t[row['date'].strftime("%d-%b")] = 1 #self.getTotalForms(row['_id'])
                    self.fwps[date_col][str(row['fwp_id'])] = 1
                    
                    if self.isAttandenceMark(row['fwp_id'],row['date']):
                        t['FWP'][date_col] = 1
                    
                    t['MIC'][date_col] = self.getTotalForms(row['_id'])
                    
                    if t['FWP'][date_col]:
                        t['MIC / FWP'][date_col] = round(t['MIC'][date_col] / t['FWP'][date_col])
                    
                    
                    self.cycle[cycle][city] = t
                
            #df = pd.DataFrame(self.cycle)
            #print(df)
            #exit() 
            
           
            
            id = ObjectId()
            #print(date)
            month = date.strftime("%b")
            #print(month)
            name = 'PMI-Dashboard-'+month+"-"+str(id)+'.xlsx'
            
            #name = 'Attandance - Oct.xlsx'
            filename = self.path+name
            
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("SUMMARY")
            
            #writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            
            # Write each dataframe to a different worksheet.
            for k in self.cycle: 
                
                rows = self.cycle[k]
               
                c = 0
                worksheet1 = workbook.add_worksheet(k)
                worksheet1.set_column(0, 4, 17)
              
                c = self.__insertWorksheet(c,k,workbook,worksheet1,rows) 
               
                
               
            workbook.close()
           
            self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})
            
          
        except Exception as e:
            print("Report Error : " + str(e)) 
    
    
    def getTotalForms(self,activity_id):
        try:
            
            """startDate  =  datetime.strptime(str(activity_date.date()),"%Y-%m-%d")
            endDate  =  datetime.strptime(str(activity_date.date()),"%Y-%m-%d")
            
            endDate = endDate + timedelta(seconds=86399) # days, seconds, then other fields."""
           
            #print(activity_id)
            #print("\n")
            c = self.db.miform.count_documents({'activity_id':activity_id})
            #print(str(activity_id) + " : "+ str(c) + "\n")
            return c
            #return result.count()
               
        except Exception as e:
            print("Form Error : " + str(e)) 
            return 0
            
    def isAttandenceMark(self,user_id,date):
        try:
            #print({'user_id':user_id,'date':date})
            c = self.db.attendance.count_documents({'user_id':user_id,'date':date})
            #print("Attandance : "+ str(c) + "\n")
            return c
            #return result.count()
               
        except Exception as e:
            print("Form Error : " + str(e)) 
            return 0        
                    
    def start(self):
        try:
            result = self.db.report_requests.find({'status':0})
            #result = self.db.report_requests.find()
            reports = []
            for row in result:
                reports.append(row)
            
            for row in reports:
                #print(row)
                if row['name'] == "Dashboard":
                    self.db.report_requests.update_one({'_id':row['_id']},{"$set":{'status':1}})
                    self.report1(row)
                    
               
        except Exception as e:
            print(e)
                
o = Dashboard()
o.start()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







