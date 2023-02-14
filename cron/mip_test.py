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
                    
        if key in range(18,24):
            temp['18-24'] = 1
        elif key in range(25,29):
            temp['25-29'] = 1
        elif key in range(30,34):
            temp['30-34'] = 1
        elif key in range(35,44):
            temp['35-44'] = 1
        else:
            temp['>44'] = 1
        return temp
    
    def getColIndex(self):
        self.col_index = self.col_index+1
        return self.col_index
        
        
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
       
       
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#ffffff'})
        header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        
        
        #worksheet.merge_range('B'+str(c+1)+':V'+str(c+1),title,tittle_format)   
        
        worksheet.merge_range('R'+str(c+1)+':V'+str(c+1),'AGE',tittle_format) 
        worksheet.merge_range('X'+str(c+1)+':AH'+str(c+1),'Offered Brand',tittle_format)    
        worksheet.merge_range('AI'+str(c+1)+':AO'+str(c+1),'Competition Brand',tittle_format)     
        
        c += 1    
        
        self.col_index = 0
       
       
                          
        worksheet.write(c, 0, 'SR.NO',self.left_format)
        
        
        
        worksheet.write(c, self.getColIndex(), 'DATE',header_format)
        worksheet.write(c, self.getColIndex(), 'DAY',header_format)
        worksheet.write(c, self.getColIndex(), 'ACTIVITY TYPE',header_format)
        
        worksheet.write(c, self.getColIndex(), 'OUTLET CODE',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET NAME',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET ADDRESS',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET AREA',header_format)
        worksheet.write(c, self.getColIndex(), 'OUTLET ZONE',header_format)
        
        worksheet.write(c, self.getColIndex(), 'FWP NAME',header_format)
        worksheet.write(c, self.getColIndex(), 'FWP CODE',header_format)
        worksheet.write(c, self.getColIndex(), 'SUPERVISOR NAME',header_format)
        worksheet.write(c, self.getColIndex(), 'SUPERVISOR CODE',header_format)
        
        worksheet.write(c, self.getColIndex(), 'ASM',header_format)
        worksheet.write(c, self.getColIndex(), 'CONTACT',header_format)
        
        worksheet.write(c, self.getColIndex(), 'FWP HEAD COUNT',header_format)
        worksheet.write(c, self.getColIndex(), 'FWP ATTENDANCE',header_format)
        
        worksheet.write(c, self.getColIndex(), '18-24',header_format)
        worksheet.write(c, self.getColIndex(), '25-29',header_format)
        worksheet.write(c, self.getColIndex(), '30-34',header_format)
        worksheet.write(c, self.getColIndex(), '35-44',header_format)
        worksheet.write(c, self.getColIndex(), '>44',header_format)
        
        worksheet.write(c, self.getColIndex(), 'How many cigarettes do you smoke in a Day?',header_format)
        
        
        for temp in self.offerProducts.values():
            worksheet.write(c, self.getColIndex(),  temp,header_format)
            
        for temp in self.products.values():
            worksheet.write(c, self.getColIndex(), temp,header_format)
        
     
        worksheet.write(c, self.getColIndex(), 'Stick design',header_format)
        worksheet.write(c, self.getColIndex(), 'Packaging',header_format)
       
        worksheet.write(c, self.getColIndex(), 'Overall likeability',header_format)
        worksheet.write(c, self.getColIndex(), 'Attempted Surveys',header_format)
        worksheet.write(c, self.getColIndex(), 'Completed Surveys',header_format)
        worksheet.write(c, self.getColIndex(), 'LAS Gender',header_format)
        
       
        
        for row in data:
            c += 1
            #print(row)
            self.__insertRow(worksheet,c,row,format2)
            
        return c+2
        
    
    # For City            
    def __insertRow(self,worksheet,c,row,cell_format):   
        try:
           
            rc = 0
            #print(row)
            #exit()
            for k in row:
                try:
                    worksheet.write(c,rc,row[k],cell_format)
                except:
                    worksheet.write(c,rc,'',cell_format)
                rc += 1
                
            #worksheet.write(c,0,srNo)
            return rc
        except Exception as e:
            print("Error - Insert Row : "+str(e))
                    
    
        
        
    
    
    def mipReport(self,req):
        try:
            dateStr = ''
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
         
            if str(req['filter']['fromDate']) == str(req['filter']['toDate']):
                aggr.append({"$match":{"date":req['filter']['fromDate']}})
                dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "")
            else:
                req['filter']['toDate'] = req['filter']['toDate'] + timedelta(days=1)
                aggr.append({"$match":{"date":{"$gte": req['filter']['fromDate'], "$lt": req['filter']['toDate']}}})
                dateStr = str(req['filter']['fromDate']).replace(" 00:00:00", "") + "-To-" + str(req['filter']['toDate']).replace(" 00:00:00", "")
             
            aggr.append({"$sort" : { "date" : 1, "outlet_id": 1,"city_id":1 } })
            print(aggr)
            result = self.db.miform.aggregate(aggr,allowDiskUse=True)
            
            city = {}
            
            c = 0
            if result:   
                for row in result:
                    
                    user = []
                    t = {}
                    try:
                        user = self.users[str(row['user_id'])]
                        age = self.getAge(row['age'])
                        
                        activity = self.getActivity(row['activity_id'])
                       
                        c = c+1
                        t = {}
                        t['SR.NO'] =  c
                        t['DATE'] = row['date'].strftime("%d-%b-%Y")
                        t['DAY'] =  row['date'].strftime('%a')
                        t['ACTIVITY TYPE'] = activity['activity']
                        
                        t['OUTLET CODE'] = row['outlet']['code']
                        t['OUTLET NAME'] = row['outlet']['name']
                        t['OUTLET ADDRESS'] = row['outlet']['address']
                        t['OUTLET AREA'] = row['outlet']['area']
                        t['OUTLET ZONE'] = row['outlet']['zone']
                        
                        t['FWP NAME'] = user['fwp_name']
                        t['FWP CODE'] = user['fwp_code']
                        t['SUPERVISOR NAME'] = user['supervisor_name']
                        t['SUPERVISOR CODE'] = user['supervisor_code']
                        
                        t['ASM'] = activity['asm']
                        t['CONTACT'] = activity['contact']
                       
                        t['FWP HEAD COUNT'] = 1
                        t['FWP ATTENDANCE'] = 1
                        
                        t['18-24'] = age['18-24']
                        t['25-29'] = age['25-29']
                        t['30-34'] = age['30-34']
                        t['35-44'] = age['35-44']
                        t['>44'] = age['>44']
                        
                        if 'avg_cigarttes' in row:
                            t['How many cigarettes do you smoke in a Day?'] = row['avg_cigarttes']
                        else:
                            t['How many cigarettes do you smoke in a Day?'] = 0
                        
                        
                        for temp in self.offerProducts.values():
                            t[temp] = 0
                            if str(row['offer_brand']) in self.offerProducts:
                                if temp == self.offerProducts[str(row['offer_brand'])]:
                                    t[temp] = 1
                        
                        
                        for temp in self.products.values():
                            t[temp] = 0
                            if str(row['brands']) in self.products:
                                if temp == self.products[str(row['brands'])]:
                                    t[temp] = 1
                        
                        
                        
                        t['Stick design'] = row['sticky_design']
                        t['Packaging'] = row['packaging']
                        t['Overall likeability'] = row['overall_likeability']
                        t['Attempted Surveys'] = 1
                        t['Completed Surveys'] = 1
                        t['LAS Gender'] = row['gender']
                      
                        
                       
                        
                        if str(row['outlet']['city_id']) in city:
                            city[str(row['outlet']['city_id'])].append(t)
                        else:   
                            city[str(row['outlet']['city_id'])] = []
                            city[str(row['outlet']['city_id'])].append(t)
                    
                        #print(t)
                        #exit()
                        
                        self.city[str(row['outlet']['city_id'])]['total'] = self.city[str(row['outlet']['city_id'])]['total'] + 1
                        
                            #print(t)
                    except Exception as e:
                        #print(row)
                        #exit()
                        print("Row Error : "+str(e))
                        pass
                    
                 
                id = ObjectId()
                name = 'MIP-'+dateStr+"-"+str(id)+'.xlsx'
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
                    worksheet1.set_column(0, 49, 20)
                    
                    
                    
                    c = self.__insertWorksheet(c,self.city[k]['name'],workbook,worksheet1,city[k])
                   
                
                workbook.close()
                
                #print({'_id':req['_id']})
                #print({"$set":{'status':3,'filename':name}})
                self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})
                
        except Exception as e:
            print("Error report : "+str(e))
            self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':2}}) 
    
    
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
                if row['name'] == "MIP":
                    #startDate = row['filter']['date'].replace(day = 1)
                    row['filter']['fromDate'] = row['filter']['date'].replace(day = 30)
                    row['filter']['toDate'] = row['filter']['date'].replace(day = calendar.monthrange(row['filter']['date'].year, row['filter']['date'].month)[1])
                    print(row)
                    #exit()
        
        
                    self.db.report_requests.update_one({'_id':row['_id']},{"$set":{'status':1}})
                    self.city = self.getCity()  
                    self.mipReport(row)
                    
               
        except Exception as e:
            print(e)
                
o = Outlet()
o.start()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







