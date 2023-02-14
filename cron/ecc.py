#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import calendar
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId
from collections import defaultdict
import pprint
from xlsxwriter.utility import xl_rowcol_to_cell,xl_col_to_name

import Lib.log
log = Lib.log.getLogger(__name__)


class Outlet:
    
    def __init__(self):
        self.mongo = MongoDb()
        self.db = self.mongo.getDb()
        
        self.city = self.getCity()   
        self.users = self.getUser()
        
        self.offerProducts,self.offerBrandCols = self.getOfferBrands()
        
        self.products,self.brandCols = self.getBrands()
        
        self.outlets = {}
        
        self.path = "/var/www/pma/uploads/reports/"   
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
       

    def getOfferBrands(self):
        try:
            productResults = self.db.offer_products.find()
            offerProducts = {}
            col = []
            values = []
            for row in productResults:
                offerProducts[str(row['_id'])] = row['name']
                col.append(('Offered Brand',row['name']))
                #values.append()
            return offerProducts,col
        except:
            return {},[]
        
    def getBrands(self):
        try:
            productResults = self.db.products.find()
            offerProducts = {}
            col = []
            values = []
            for row in productResults:
                offerProducts[str(row['_id'])] = row['name']
                col.append(('Competition Brand',row['name']))
                #values.append()
            return offerProducts,col
        except:
            return {},[]
    
    
    
    def getAge(self,age): 
        temp = {'18-24':0,'25-29':0,'30-34':0,'35-44':0,'>44':0}
        key = int(age)
                    
        if key in range(18,25):
            temp['18-24'] = 1
        elif key in range(25,30):
            temp['25-29'] = 1
        elif key in range(30,35):
            temp['30-34'] = 1
        elif key in range(35,45):
            temp['35-44'] = 1
        else:
            temp['>44'] = 1
        return temp
    
    def getColIndex(self):
        self.col_index = self.col_index+1
        return self.col_index
        
        
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
       
       
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#ffffff'})
        header_format = workbook.add_format({'align':'left','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'left','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'align':'left','bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'align':'left','bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        
        
        #worksheet.merge_range('B'+str(c+1)+':V'+str(c+1),title,tittle_format)   
        
        worksheet.merge_range('G'+str(c+1)+':I'+str(c+1),'TOTAL PRODUCTIVITY SUMMARY',tittle_format) 
        worksheet.merge_range('J'+str(c+1)+':O'+str(c+1),'AGE SPLIT',tittle_format) 
        worksheet.merge_range('P'+str(c+1)+':W'+str(c+1),'COMPETITION BRAND SPLIT',tittle_format) 
        worksheet.merge_range('X'+str(c+1)+':AI'+str(c+1),'OFFER BRAND',tittle_format) 
        #worksheet.merge_range(':'+str(c+1)+':V'+str(c+1),'COMPETITION BRAND SPLIT',tittle_format)    
        """worksheet.merge_range('AI'+str(c+1)+':AO'+str(c+1),'Competition Brand',tittle_format)   """  
        
        c += 1    
        
        self.col_index = 0
       
       
                          
        #worksheet.write(c, 0, 'SR.NO',self.left_format)
        
      
        worksheet.write(c, 0, 'OUTLET CODE',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET NAME',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET ADDRESS',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET AREA',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET ZONE',header_format)
        
        worksheet.write(c, self.getColIndex(), 'CITY',header_format)
        worksheet.write(c, self.getColIndex(), 'GRAND TOTAL',header_format)
        worksheet.write(c, self.getColIndex(), 'NO. OF VISITS',header_format)
        worksheet.write(c, self.getColIndex(), 'AVG. CONTACTS',header_format)
                    
                    
        worksheet.write(c, self.getColIndex(), '18-24',header_format)
        worksheet.write(c, self.getColIndex(), '25-29',header_format)
        worksheet.write(c, self.getColIndex(), '30-34',header_format)
        worksheet.write(c, self.getColIndex(), '35-44',header_format)
        worksheet.write(c, self.getColIndex(), '>44',header_format)
        worksheet.write(c, self.getColIndex(), 'TOTAL',header_format)
        
        
        for temp in self.products.values():
            worksheet.write(c, self.getColIndex(), temp,header_format)
            
        worksheet.write(c, self.getColIndex(), 'TOTAL',header_format)
        
        for temp in self.offerProducts.values():
            worksheet.write(c, self.getColIndex(),  temp,header_format)
            
        worksheet.write(c, self.getColIndex(), 'TOTAL',header_format)
            
        """worksheet.write(c, self.getColIndex(), 'How many cigarettes do you smoke in a Day?',header_format)
        
        
        for temp in self.offerProducts.values():
            worksheet.write(c, self.getColIndex(),  temp,header_format)
            
        for temp in self.products.values():
            worksheet.write(c, self.getColIndex(), temp,header_format)
        
     
        worksheet.write(c, self.getColIndex(), 'Stick design',header_format)
        worksheet.write(c, self.getColIndex(), 'Packaging',header_format)
       
        worksheet.write(c, self.getColIndex(), 'Overall likeability',header_format)
        worksheet.write(c, self.getColIndex(), 'Attempted Surveys',header_format)
        worksheet.write(c, self.getColIndex(), 'Completed Surveys',header_format)
        worksheet.write(c, self.getColIndex(), 'LAS Gender',header_format)"""
        
       
        try:
            for row in data:
                c += 1
                #print(row)
                self.__insertRow(worksheet,c,data[row],format2)
                
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
                try:
                    worksheet.write(c,rc,row[k],cell_format)
                    
                    if k == 'AGE TOTAL':
                        worksheet.write(c,rc,"=SUM(J"+str(c+1)+":"+"N"+str(c+1)+")",cell_format)
                    if k == 'PRODUCT TOTAL':
                        worksheet.write(c,rc,"=SUM(P"+str(c+1)+":"+"V"+str(c+1)+")",cell_format)
                    if k == 'OFFER PRODUCT TOTAL':
                        worksheet.write(c,rc,"=SUM(X"+str(c+1)+":"+"AH"+str(c+1)+")",cell_format)
                    
                except:
                    worksheet.write(c,rc,'',cell_format)
                    
                
                rc += 1
                
            #worksheet.write(c,0,srNo)
            return rc
        except Exception as e:
            print("Error - Insert Row : "+str(e))
                    
    
        
    def productivityReport(self,req):    
        try:
            dateStr = ''
            
            
            
            #result = self.db.outlet_activity.aggregate(aggr,allowDiskUse=True)
            
            """aggr = {}
         
            if str(req['filter']['fromDate']) == str(req['filter']['toDate']):
                aggr["date"] = req['filter']['fromDate']
                dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "")
            else:
                aggr["date"] = {"$gte": req['filter']['fromDate'], "$lt": req['filter']['toDate']}
                dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "") + "-To-" + str(req['filter']['toDate']).replace(" 00:00:00", "")
             
            #aggr["$sort"] = { "date" : 1, "outlet_id": 1}
            aggr["outlet_id"] = ObjectId("5e3a86aedb92f0d369dc3f64")
            #result = self.db.outlet_activity.find(aggr).skip(0).limit(200)
            print(aggr)
            #exit()
            result = self.db.outlet_activity.find(aggr)"""
            
            tt = {}
            tt['OUTLET CODE'] = ""
            tt['OUTLET NAME'] = ""
            tt['OUTLET ADDRESS'] = ""
            tt['OUTLET AREA'] = ""
            tt['OUTLET ZONE'] = ""
            tt['CITY'] = ""
            
            tt['GRAND TOTAL'] = 0
            tt['NO. OF VISITS'] = 0
            tt['AVG. CONTACTS'] = 0
            tt['18-24'] = 0
            tt['25-29'] = 0
            tt['30-34'] = 0
            tt['35-44'] = 0
            tt['>44'] = 0
            tt['AGE TOTAL'] = 0
            
            
            for temp in self.products.values():
                tt[temp] = 0
            tt['PRODUCT TOTAL'] = 0
                
            for temp in self.offerProducts.values():
                tt[temp] = 0
            tt['OFFER PRODUCT TOTAL'] = 0
            
            #Excel function start 
            id = ObjectId()
            name = 'ECC-'+dateStr+"-"+str(id)+'.xlsx'
            filename = self.path+name
            
            #writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("SUMMARY")
         
            header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
            self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#ffffff'})
            
            #Excel function End
                       
            data = {}
            
            activities = ["MI","LAMPS","NOW","RAP"]
            
            for activity in activities:
                aggr = {}
                aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
         
                if str(req['filter']['fromDate']) == str(req['filter']['toDate']):
                    aggr.append({"$match":{"date":req['filter']['fromDate']}})
                    dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "")
                else:
                    aggr.append({"$match":{"date":{"$gte": req['filter']['fromDate'], "$lt": req['filter']['toDate']}}})
                    dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "") + "-To-" + str(req['filter']['toDate']).replace(" 00:00:00", "")
                
                #aggr.append({"$match":{"outlet_id":ObjectId("5e3a86aedb92f0d369dc3f64")}})
                         
                
                aggr.append({"$match":{"activity":activity}})
                aggr.append({"$sort" : { "date" : 1}})
                #print(aggr)
                result = self.db.outlet_activity.aggregate(aggr,allowDiskUse=True)
                self.outlets = {}
                
                if result:   
                    for row in result:
                        
                        t = tt.copy()
                        t['OUTLET CODE'] = row['outlet']['code']
                        t['OUTLET NAME'] = row['outlet']['name']
                        t['OUTLET ADDRESS'] = row['outlet']['address']
                        t['OUTLET AREA'] = row['outlet']['area']
                        t['OUTLET ZONE'] = row['outlet']['zone']
                        t['CITY'] = self.city[str(row['outlet']['city_id'])]['name']
                        
                        if str(row['outlet_id']) in self.outlets:
                            t = self.outlets[str(row['outlet_id'])]
                        else:
                            self.outlets[str(row['outlet_id'])] = t
                        
                        t['NO. OF VISITS'] = t['NO. OF VISITS'] + 1
                        
                        tr = self.getOutletWise(row['_id'],t)
                        
                        #pprint.pprint(tr)   
                        if tr:
                            self.outlets[str(row['outlet_id'])] = tr
                       
                    worksheet1 = workbook.add_worksheet("Outlet Wise "+activity)
                    worksheet1.set_column(0, 49, 20)
                    c = 0        
                    c = self.__insertWorksheet(c,"Outlet Wise "+activity,workbook,worksheet1,self.outlets)
                    
            #pprint.pprint(self.outlets)   
            #exit() 
            #df = pd.DataFrame(self.outlets)
            #print(df)        
            
            
            
            
                   
                
            workbook.close()
            self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})    
            
        except Exception as e:
            print("ProductivityReport function Error : "+str(e))
            self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':2}}) 
    
    
    
            
    def getOutletWise(self,activity_id,t):
        try:
            aggr = {}
            aggr["activity_id"] = activity_id 
            
            result = self.db.miform.find(aggr)
            
            if result:   
                for row in result:
                    age = self.getAge(row['age'])
                  
                    t['GRAND TOTAL'] = t['GRAND TOTAL']+1
                    t['AVG. CONTACTS'] = t['AVG. CONTACTS']+1
                    
                    t['18-24'] = t['18-24'] + age['18-24']
                    t['25-29'] = t['25-29'] + age['25-29']
                    t['30-34'] = t['30-34'] + age['30-34']
                    t['35-44'] = t['35-44'] + age['35-44']
                    t['>44'] = t['>44'] + age['>44']
                    
                    temp = self.products[str(row['brands'])]
                    t[temp] = t[temp] + 1
                    
                    temp = self.offerProducts[str(row['offer_brand'])]
                    t[temp] = t[temp] + 1
                    
                return t
            else:
                return False
                    
            
        except Exception as e:
            print("getOutletWise Error : "+str(e))
            return False
    
    
    def getActivity(self,id):
        try:
            #print({'user_id':user_id,'date':date})
            result = self.db.outlet_activity.find({'_id':id})
            if result:
                for row in result:
                    return row
            
            return False
            
               
        except Exception as e:
            print("activity Error : " + str(e)) 
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
                if row['name'] == "ECC":
                    #startDate = row['filter']['date'].replace(day = 1)
                    row['filter']['fromDate'] = row['filter']['date'].replace(day = 1)
                    row['filter']['toDate'] = row['filter']['date'].replace(day = calendar.monthrange(row['filter']['date'].year, row['filter']['date'].month)[1])
        
        
                    self.db.report_requests.update_one({'_id':row['_id']},{"$set":{'status':1}})
                    self.city = self.getCity()  
                    self.productivityReport(row)
                    
               
        except Exception as e:
            print(e)
                
o = Outlet()
o.start()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







