#!/usr/local/bin/python3
from Lib.mongoDb import MongoDb
import sys
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter
from bson import ObjectId


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

    def activeOutletReport(self,req):
        try:
            
            #self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            #self.dateInput = datetime.strptime("2019-12-14","%Y-%m-%d")
            date = req['filter']['date']
            #print(date)
            self.dateInput = date
            dateStr = str(date).replace(" 00:00:00", "")
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            #aggr.append({"$match":{"date":self.dateInput}})
            aggr.append({"$sort" : { "date" : 1, "outlet_id": 1,"city_id":1 } })
            aggr.append({ "$limit" : 3 })
            #result = self.db.outlet_activity.aggregate(aggr)
        
            result = self.db.miform.aggregate(aggr)
           
           
           
            city = {}
            
            columns = ['SR.NO','DATE','DAY','ACTIVITY TYPE','OUTLET CODE','OUTLET NAME','OUTLET ADDRESS','AREA','SUPERVISOR NAME','SUPERVISOR CODE','FWP NAME','FWP CODE','FWP HEAD COUNT','FWP ATTENDANCE']
            
            c = 0
            if result:   
                for row in result:
                    try:
                        #print(str(c)+" : "+str(row['_id'])+"\n")
                        
                        c = c+1 #'=ROW()−1'
                        #user,supervisor = self.getUser(row['user_id'])
                        user = self.users[str(row['user_id'])]
                        supervisor = self.users[str(user['parent'])]
                        
                        t = {}
                        t['SR.NO'] =  c
                        t['DATE'] = str(row['date'])
                        t['DAY'] =  row['date'].strftime('%A')
                        t['ACTIVITY TYPE'] = ''
                      
                        t['OUTLET CODE'] = row['outlet']['code']
                        t['OUTLET NAME'] = row['outlet']['name']
                        t['OUTLET ADDRESS'] = row['outlet']['address']
                        t['AREA'] = row['outlet']['area']
                        t['SUPERVISOR NAME'] = supervisor['name']
                        t['SUPERVISOR CODE'] = supervisor['code']
                        t['FWP NAME'] = user['name']
                        t['FWP CODE'] = user['code']
                        t['FWP HEAD COUNT'] = 1
                        t['FWP ATTENDANCE'] = 1
                        
                        
                        if str(row['outlet']['city_id']) in city:
                            city[str(row['outlet']['city_id'])].append(t)
                        else:   
                            city[str(row['outlet']['city_id'])] = []
                            #city[str(row['outlet']['city_id'])].append(columns)
                            city[str(row['outlet']['city_id'])].append(t)
                    except Exception as e:
                        print("Error Iterate : "+ str(e) + "\n")
                    
                    #print(city)    
                    #print(t)
                    #exit()
                
                #print(city)
                id = ObjectId()
                name = 'MIP-Report-'+dateStr+"-"+str(id)+'.xlsx'
                filename = self.path+name
                
                writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                workbook = writer.book
                
                # Write each dataframe to a different worksheet.
                for k in city.keys(): 
                    df1 = pd.DataFrame(city[k],columns=columns,index=columns)
                    #df1 = pd.DataFrame(city[k])
                    #df1 = df1.set_index('FWP HEAD COUNT', append=True).swaplevel(0,1)
                    #df1 = df1.set_index('FWP ATTENDANCE', append=True).swaplevel(0,1)
                   
                    df1.to_excel(writer, sheet_name=self.city[k],index=False)
                    
                    
                    workbook=writer.book
                    worksheet = writer.sheets[self.city[k]]
                    
                    header_format = workbook.add_format({'bold': True,'text_wrap': False,'valign': 'top','align':'center','fg_color': '#d95450','font_color':'#ffffff','border': 1})
                    body_format = workbook.add_format({'valign': 'middle','align':'center'})
                    
                    # Write the column headers with the defined format.
                    for col_num, value in enumerate(df1.columns.values):
                        worksheet.write(0, col_num, value, header_format)

                    worksheet.set_column('A:M', None, body_format) 
                    
                    for idx, col in enumerate(df1):  # loop through all columns
                        series = df1[col]
                        max_len = max((series.astype(str).map(len).max(), len(str(series.name)))) + 2 
                        worksheet.set_column(idx, idx, max_len)  # set column width
                        
                    print(df1)    
                        #merge_format = workbook.add_format({'align': 'center'})
                        #worksheet.merge_range('B3:D4', 'Merged Cells', merge_format)
                 
                    
            
              
                writer.save()
                        #print(row)
                #print({'_id':req['_id']})
                #print({"$set":{'status':3,'filename':name}})
                #self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})
                
        except Exception as e:
            print("Error : "+ str(e) + "\n")
    
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
     
    def mipReport(self,req):
        try:
            
            #self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            #self.dateInput = datetime.strptime("2019-12-14","%Y-%m-%d")
            date = req['filter']['date']
            #print(date)
            self.dateInput = date
            dateStr = str(date).replace(" 00:00:00", "")
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            #aggr.append({"$match":{"date":self.dateInput}})
            aggr.append({"$sort" : { "date" : 1, "outlet_id": 1,"city_id":1 } })
            aggr.append({ "$limit" : 5 })
            #result = self.db.outlet_activity.aggregate(aggr)
        
            result = self.db.miform.aggregate(aggr)
           
           
           
            city = {}
            
            columns = ['SR.NO','DATE','DAY','ACTIVITY TYPE','OUTLET CODE','OUTLET NAME','OUTLET ADDRESS','AREA','SUPERVISOR NAME','SUPERVISOR CODE','FWP NAME','FWP CODE','FWP HEAD COUNT','FWP ATTENDANCE','18-24','24-32']
            
            L = [('','SR.NO'), ('','DATE'),('','DAY'),('','ACTIVITY TYPE'),('','OUTLET CODE'),('','OUTLET NAME'),
                 ('','OUTLET ADDRESS'),('','AREA'),('','SUPERVISOR NAME'),('','SUPERVISOR CODE'),('','FWP NAME'),('','FWP CODE'),('','FWP HEAD COUNT'),
                ('','FWP ATTENDANCE'),('AGE','18-24'),('AGE','25-29'),('AGE','30-34'),('AGE','35-44'),('AGE','>44'),('','How many cigarettes do you smoke in a Day?'),
                ('Rate the following attributes on a scale of 1 to 5','Stick design'),('Rate the following attributes on a scale of 1 to 5','Packaging'),('Rate the following attributes on a scale of 1 to 5','Overall likeability'),
                ('','Attempted Surveys'),('','Completed Surveys'),('','LAS Gender')]
            #L = [('AGE','18-24','24-32')]
            c = 0
            if result:   
                for row in result:
                    try:
                        #print(str(c)+" : "+str(row['_id'])+"\n")
                        
                        c = c+1 #'=ROW()−1'
                        #user,supervisor = self.getUser(row['user_id'])
                        user = self.users[str(row['user_id'])]
                        supervisor = self.users[str(user['parent'])]
                        age = self.getAge(row['age'])
                        
                        t = {}
                        t['SR.NO'] =  c
                        t['DATE'] = str(row['date'])
                        t['DAY'] =  row['date'].strftime('%A')
                        t['ACTIVITY TYPE'] = ''
                      
                        t['OUTLET CODE'] = row['outlet']['code']
                        t['OUTLET NAME'] = row['outlet']['name']
                        t['OUTLET ADDRESS'] = row['outlet']['address']
                        t['AREA'] = row['outlet']['area']
                        t['SUPERVISOR NAME'] = supervisor['name']
                        t['SUPERVISOR CODE'] = supervisor['code']
                        t['FWP NAME'] = user['name']
                        t['FWP CODE'] = user['code']
                        t['FWP HEAD COUNT'] = 1
                        t['FWP ATTENDANCE'] = 1
                        t['18-24'] = age['18-24']
                        t['25-29'] = age['25-29']
                        t['30-34'] = age['30-34']
                        t['35-44'] = age['35-44']
                        t['>44'] = age['>44']
                        t['How many cigarettes do you smoke in a Day?'] = row['avg_cigarttes']
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
                            #city[str(row['outlet']['city_id'])].append(columns)
                            city[str(row['outlet']['city_id'])].append(t)
                    except Exception as e:
                        print("Error Iterate : "+ str(e) + "\n")
                    
                    #print(city)    
                    #print(t)
                    #exit()
                
                #print(city)
                id = ObjectId()
                name = 'MIP-Report-'+dateStr+"-"+str(id)+'.xlsx'
                filename = self.path+name
                
                writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                workbook = writer.book
                
                # Write each dataframe to a different worksheet.
                for k in city.keys(): 
                    df1 = pd.DataFrame(city[k])
                    
                    df1.columns = pd.MultiIndex.from_tuples(L)
                    
                    df1.to_excel(writer, sheet_name=self.city[k],index=True)
                    
                    
                    workbook=writer.book
                    worksheet = writer.sheets[self.city[k]]
                    
                    header_format = workbook.add_format({'bold': True,'text_wrap': False,'valign': 'top','align':'center','fg_color': '#d95450','font_color':'#ffffff','border': 1})
                    body_format = workbook.add_format({'valign': 'middle','align':'center'})
                    
                    # Write the column headers with the defined format.
                    worksheet.write(1, 0, '', header_format)
                    for col_num, value in enumerate(L):
                        l,name = value
                        worksheet.write(1, col_num+1, name, header_format)

                    worksheet.set_column('A:M', None, body_format) 
                    
                    for idx, col in enumerate(df1):  # loop through all columns
                        series = df1[col]
                        l,name = series.name
                        #print(name)
                        
                        max_len = max((series.astype(str).map(len).max(), len(str(name)))) + 1
                        worksheet.set_column(idx, idx, 10)  # set column width
                        
                    #print(df1)    
                        #merge_format = workbook.add_format({'align': 'center'})
                        #worksheet.merge_range('B3:D4', 'Merged Cells', merge_format)
                 
                    
            
              
                writer.save()
                        #print(row)
                #print({'_id':req['_id']})
                #print({"$set":{'status':3,'filename':name}})
                #self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})
                
        except Exception as e:
            print("Error : "+ str(e) + "\n") 
            
    def start(self):
        try:
            result = self.db.report_requests.find({'status':0})
            #result = self.db.report_requests.find()
            reports = []
            for row in result:
                reports.append(row)
            
            for row in reports:
                
                if row['name'] == "MIP":
                    #print(row)
                    #self.db.report_requests.update_one({'_id':row['_id']},{"$set":{'status':1}})
                    #self.activeOutletReport(row)
                    self.mipReport(row)
                    
               
        except Exception as e:
            print(e)
 
 
"""df = pd.DataFrame({
        'A':list('abcdef'),
         'B':[4,5,4,5,5,4],
         'C':[7,8,9,4,2,3],
         'D':[1,3,5,7,1,0],
         'E':[5,3,6,9,2,4],
         'F':list('aaabbb')
})

L = [('OBS','A','C'), ('FIN', 'D','F')]

cols = [(new, c) for new, start, end in L for c in df.loc[:, start:end].columns]
df.columns = pd.MultiIndex.from_tuples(cols)
print (cols)

writer = pd.ExcelWriter("test.xlsx", engine='xlsxwriter')
df.to_excel(writer, sheet_name='test')          
#df.columns = pd.MultiIndex.from_tuples(zip(df.columns, ["DD", "EE", "FF"]))                    
print(df)
writer.save()"""
             
o = Outlet()
o.start()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")






