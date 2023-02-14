#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId
from collections import defaultdict


import Lib.log
log = Lib.log.getLogger(__name__)


class Outlet:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        
        #self.city = self.getCity()   
        self.users = self.getUser()
       
        #self.path = "/var/www/pma/uploads/reports/"   
        #self.path = "/var/www/pmitest.redtons.com/uploads/reports/"   
        self.path = "/usr/share/www/liveApi/uploads/reports/"   
        
    def getCity(self):
        result = self.db.city.find()
        city = {}
        for row in result:
            city[str(row['_id'])] = {'name':row['name'],'total':0}
        city['False'] = {'name':'No City','total':0}
        return city   
            
    def getUser(self):
        
        aggr = [{"$lookup": { "from": "users", "localField": "parent_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"}]
        result = self.db.users.aggregate(aggr)
        self.users = {}
        for row in result:
            self.users[str(row['_id'])] = {'fwp_name':row['name'],'fwp_code':row['code'],'supervisor_name':row['user']['name'],'supervisor_code':row['user']['code']}
        return self.users
        """result = self.db.users.find_one({'_id':id})
        user = {}
        user['name'] = ''
        user['code'] = ''
        if result:
            user['name'] = result['name']
            user['code'] = result['code']
        return user"""


    def __insertWorksheet(self,c,title,workbook,worksheet,data):
       
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        
        
        worksheet.merge_range('B'+str(c+1)+':V'+str(c+1),title,tittle_format)   
        
        c += 1    
       
        worksheet.write(c,0,'SR.NO',self.left_format)
        worksheet.write(c,1,'DATE',header_format)
        worksheet.write(c,2,'CHECKIN TIME',header_format)
        worksheet.write(c,3,'LATITUDE',header_format)
        worksheet.write(c,4,'LONGITUDE',header_format)
        worksheet.write(c,5,'DAY',header_format)
        worksheet.write(c,6,'TIME',header_format)
        worksheet.write(c,7,'OUTLET CODE',header_format)
        worksheet.write(c,8,'OUTLET NAME',header_format)
        worksheet.write(c,9,'OUTLET ADDRESS',header_format)
        worksheet.write(c,10,'FWP NAME',header_format)
        worksheet.write(c,11,'FWP CODE',header_format)
        worksheet.write(c,12,'SUPERVISOR NAME',header_format)
        worksheet.write(c,13,'SUPERVISOR CODE',header_format)
        worksheet.write(c,14,'ACTIVE',header_format)
        worksheet.write(c,15,'ZONE',header_format)
        worksheet.write(c,16,'CONTACT',header_format)
        worksheet.write(c,17,'TSE',header_format)
        worksheet.write(c,18,'ASM',header_format)
        worksheet.write(c,19,'MEETING',header_format)
        worksheet.write(c,20,'ACTIVITY',header_format)
        worksheet.write(c,21,'CYCLE',header_format)
        
        
        for row in data:
            c += 1
            self.__insertRow(worksheet,c,row,format1,format2)
            
        return c+2
        
            
    def __insertRow(self,worksheet,c,row,format1,format2):   
        if (c % 2) == 0:  
            worksheet.set_row(c, cell_format=format1)
        else:
            worksheet.set_row(c, cell_format=format2) 
        
        worksheet.write(c,0,(c-1))
        worksheet.write(c,1,row['DATE'])
        worksheet.write(c,2,row['CHECKIN TIME'])
        worksheet.write(c,3,row['LATITUDE'])
        worksheet.write(c,4,row['LONGITUDE'])
        worksheet.write(c,5,row['DAY'])
        worksheet.write(c,6,row['TIME'])
        worksheet.write(c,7,row['OUTLET CODE'])
        worksheet.write(c,8,row['OUTLET NAME'])
        worksheet.write(c,9,row['OUTLET ADDRESS'])
        worksheet.write(c,10,row['FWP NAME'])
        worksheet.write(c,11,row['FWP CODE'])
        worksheet.write(c,12,row['SUPERVISOR NAME'])
        worksheet.write(c,13,row['SUPERVISOR CODE'])
        worksheet.write(c,14,row['ACTIVE'])
        worksheet.write(c,15,row['ZONE'])
        worksheet.write(c,16,row['CONTACT'])
        worksheet.write(c,17,row['TSE'])
        worksheet.write(c,18,row['ASM'])
        worksheet.write(c,19,row['MEETING'])
        worksheet.write(c,20,row['ACTIVITY'])
        worksheet.write(c,21,row['CYCLE'])
        
        
        
    def activeOutletReport(self,req):
        try:
            dateStr = ''
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            
            if str(req['filter']['fromDate']) == str(req['filter']['toDate']):
                aggr.append({"$match":{"date":req['filter']['fromDate']}})
                dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "")
            else:
                aggr.append({"$match":{"date":{"$gte": req['filter']['fromDate'], "$lt": req['filter']['toDate']}}})
                dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "") + "-To-" + str(req['filter']['toDate']).replace(" 00:00:00", "")
                
            #print(aggr)
            #query['date'] = {"$gte": fromDate1, "$lt": toDate1}
            
            
            result = self.db.outlet_activity.aggregate(aggr)
            
            city = {}
            
          
            c = 0
            if result:   
                for row in result:
                    user = []
                    t = {}
                    try:
                        user = self.users[str(row['fwp_id'])]
                        checkin_coordinates = ''
                        checkin_time = ''
                        
                        for ac in row['checkin_activity']:
                            start = ac['start']
                            checkin_time = start['date'].strftime("%I:%M:%S %p")
                            checkin_coordinates = start['coardinates']
                            
                        if checkin_coordinates != '': 
                            c = c+1
                            t = {}
                            t['SR.NO'] =  c
                            t['DATE'] = row['date'].strftime("%d-%b-%Y")
                            t['CHECKIN TIME'] = checkin_time
                            t['LATITUDE'] = checkin_coordinates['latitude']
                            t['LONGITUDE'] = checkin_coordinates['longitude']
                            t['DAY'] =  row['date'].strftime('%a')
                            t['TIME'] = str(row['start_time'])+' - '+str(row['end_time'])
                            t['OUTLET CODE'] = row['outlet']['code']
                            t['OUTLET NAME'] = row['outlet']['name']
                            t['OUTLET ADDRESS'] = row['outlet']['address']
                            t['FWP NAME'] = user['fwp_name']
                            t['FWP CODE'] = user['fwp_code']
                            t['SUPERVISOR NAME'] = user['supervisor_name']
                            t['SUPERVISOR CODE'] = user['supervisor_code']
                            t['ACTIVE'] = 'YES'
                            t['ZONE'] = row['outlet']['zone']
                            t['CONTACT'] = row['contact']
                            t['TSE'] = row['tse']
                            t['ASM'] = row['asm']
                            t['MEETING'] = row['meeting']
                            t['ACTIVITY'] = row['activity']
                            t['CYCLE'] = row['cycle']
                           
                            if str(row['outlet']['city_id']) in city:
                                city[str(row['outlet']['city_id'])].append(t)
                            else:   
                                city[str(row['outlet']['city_id'])] = []
                                city[str(row['outlet']['city_id'])].append(t)
                        
                        
                            self.city[str(row['outlet']['city_id'])]['total'] = self.city[str(row['outlet']['city_id'])]['total'] + 1
                            
                            #print(t)
                    except Exception as e:
                        print("Row Error : "+str(e))
                        pass
                    
                 
                id = ObjectId()
                name = 'Active Outlet List-'+dateStr+"-"+str(id)+'.xlsx'
                filename = self.path+name
                
                #writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                
                workbook = xlsxwriter.Workbook(filename)
                worksheet = workbook.add_worksheet("SUMMARY")
             
                header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
                self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#ffffff'})
                
                
               
                
                c = 0
                worksheet.merge_range('A'+str(c+1)+':B'+str(c+1),"SUMMARY",self.left_format)   
                c += 1
                worksheet.write(c,0,'CITY NAME',header_format)
                worksheet.write(c,1,'TOTAL OUTLETS',header_format)
                for k in self.city:
                    row = self.city[k]
                    c += 1
                    worksheet.write(c,0,row['name'],self.left_format)
                    worksheet.write(c,1,row['total'])
                    
             
                worksheet.set_column(0, 1, 25)
                
                
                # Write each dataframe to a different worksheet.
                for k in city.keys(): 
                    c = 0
                    worksheet1 = workbook.add_worksheet(self.city[k]['name'])
                    worksheet1.set_column(0, 17, 17)
                    
                    c = self.__insertWorksheet(c,self.city[k]['name'],workbook,worksheet1,city[k])
                   
                
                workbook.close()
                
                #print({'_id':req['_id']})
                #print({"$set":{'status':3,'filename':name}})
                self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})
                
        except Exception as e:
            print("Error : "+str(e))
            self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':2}})
     
     
     
            
    def start(self):
        try:
            result = self.db.report_requests.find({'status':0})
            #result = self.db.report_requests.find()
            reports = []
            for row in result:
                reports.append(row)
            
            for row in reports:
                #print(row)
                if row['name'] == "ActiveOutlets":
                    self.db.report_requests.update_one({'_id':row['_id']},{"$set":{'status':1}})
                    self.city = self.getCity()  
                    self.activeOutletReport(row)
                    
               
        except Exception as e:
            print(e)
                
o = Outlet()
o.start()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")






