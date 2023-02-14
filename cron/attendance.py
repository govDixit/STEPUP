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
        self.roles = {1:'FWP',2:'SUPERVISOR',3:'CITY MANAGER',4:'IPM'}
        self.city = self.getCity() 
        #self.dates = self.getDays()  
        #print(self.dates)
        #print(self.row)
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
        self.columns = ['SR.NO','FWP NAME','CITY','DESIGNATION','EMP CODE']
        self.row = {}
        self.row['SR.NO'] = ''
        self.row['FWP NAME'] = ''
        self.row['CITY'] = ''
        self.row['DESIGNATION'] = ''
        self.row['EMP CODE'] = ''
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
            self.columns.append(d.strftime("%d %b %Y"))
            # ~ self.row[d.strftime("%d-%b")] = '-'
            self.row[d.strftime("%d")+"-Timestamp"] = '-'
            self.row[d.strftime("%d")+"-Coordinates"] = '-'
            self.row[d.strftime("%d")+"-Check-In"] = '-'
            self.row[d.strftime("%d")+"-Check-Out"] = '-'
            self.row[d.strftime("%d")+"-Working Hrs"] = '-'
            
            
        self.row['TOTAL'] = ''
        self.row['DOJ'] = ''
        self.row['WORKING STATUS'] = ''
        self.row['WORKING HOURS'] = ''
        
        return dates
        
    
    def __insertWorksheet(self, c, title, workbook, worksheet, data, bg_clr, bg_txt_clr, date):
        
        try:
            # ~ tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
            tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#3c4146','bg_color':bg_clr,'border':1,'border_color':'#3c4146'}) 
            date_tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#3c4146','bg_color':bg_txt_clr,'border':1,'border_color':'#3c4146'}) 
            # ~ header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
            header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#00000','bg_color':bg_clr})
            
            # ~ self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
            self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#3c4146','bg_color':bg_txt_clr,'border':1,'border_color':'#3c4146'})
            self.left_format.set_text_wrap()
            
            self.total_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#3c4146','border':2,'border_color':'#3c4146'})
            
            format1 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
            format2 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
            
            # ~ worksheet.merge_range('B'+str(c+1)+':AJ'+str(c+1),title,tittle_format)   
            worksheet.merge_range('A'+str(c+1)+':E'+str(c+1), title, tittle_format)   
            
            ## to add date heading for each attendance detail
            if title == 'FWPs ATTENDANCE' or title == 'SUPERVISORS ATTENDANCE':
                date1 = datetime.strptime(str(date.date()),"%Y-%m-%d")
                startDate = date1.replace(day=1)
                endDate = date1.replace(day = calendar.monthrange(date1.year, date1.month)[1])
                
                self.startDate = startDate
                self.endDate = endDate
                
                dates = []
                dd = 5
                eed = c
                
                for n in range(int ((endDate - startDate).days)+1):
                    d = startDate + timedelta(n)
                    dates.append(d)
                    worksheet.merge_range(eed, dd, eed, dd+4, d.strftime("%d %b %Y"), date_tittle_format)   
                    dd += 5
            ## to add date heading for each attendance detail
            
            # ~ c += 2   
            c += 1   
            
            rc = 0
            
            for r in self.row:
                worksheet.set_row(c, 28)  # Set the height of Row 1 to 20.
                worksheet.write(c, rc, r, self.left_format)
                rc += 1
            
            srNo = 0
            startC = c + 2
            for row in data:
                c += 1
                srNo += 1
                self.__insertRow(worksheet, startC, c, srNo, row, format1, format2)
                
           
            return c+3
        except Exception as e:
            print("Error - Insert Worksheet : "+str(e))
            
  
                
    def __insertRow(self, worksheet, startC, c, srNo, row, format1, format2):   
        try:
            
            if (c % 2) == 0:  
                worksheet.set_row(c, cell_format=format1)
            else:
                worksheet.set_row(c, cell_format=format2) 
            
            rc = 0
            for k in row:
                
                if k == "WORKING HOURS":
                    try:
                        row[k] = round((row[k] / 60) / 60)
                    except:
                        print(row[k])
                
                worksheet.write(c,rc,row[k])
                if k == 'TOTAL':
                    cell = xl_col_to_name((rc-1))
                    cell1 = xl_col_to_name((rc))
                    #print(cell)
                    worksheet.write(c,rc,"=SUM(F"+str(c+1)+":"+str(cell)+str(c+1)+")")
                    worksheet.write(c+1,rc,"=SUM("+str(cell1)+str(startC)+":"+str(cell1)+str(c+1)+")",self.total_format) 
                rc += 1
            worksheet.write(c, 0, srNo)
        except Exception as e:
            print("Error - Insert Row : "+str(e))
        
        
        
    def getActivity(self,data):
        start = '';
        end = '';
        #print(data)
        timestamp = ''
        coordinates = ''
        check_in = ''
        check_out = ''
        
        try:
            for row in data:
                #print(row['start'])
                start1 = row['start']
                end1 = row['end']
                
                if start == '':
                    start = str(start1['date'])
                    c =  start1['coardinates']
                    check_in = "Lat: "+str(c['latitude']) + ' Long: ' + str(c['longitude'])
                if end1['date'] != None:
                    end   = str(end1['date'])
                    c =  end1['coardinates']
                    check_out = "Lat: "+str(c['latitude']) + ' Long: ' + str(c['longitude'])
            
            timestamp =  start+' / '+end 
            return (timestamp,check_in,check_out,start,end)
        except Exception as e:
            print("getActivity Error : " + str(e))
            return (timestamp,check_in,check_out,start,end)
        
    
    def getRoutePlan(self):
        try:
            #result = self.db.outlet_activity.find({"date":{"$gte":self.startDate,"$lte":self.endDate} }).skip(0).limit(100).sort([('date', 1)])
            result = self.db.outlet_activity.find({"date":{"$gte":self.startDate,"$lte":self.endDate} })
            self.routePlans = defaultdict(lambda: defaultdict(list))
            
            for row in result:
                d = row['date']
                timestamp,check_in,check_out,start,end = self.getActivity(row['checkin_activity'])
                #print(timestamp,check_in,check_out)
                self.routePlans[d.strftime("%d-%b")][str(row['fwp_id'])] = (timestamp,check_in,check_out,start,end)
                
                #print(self.routePlans[d.strftime("%d-%b")][str(row['fwp_id'])])
        except Exception as e:
            print("getRoutePlan Error : " + str(e))
            #return ''
    
    def getSupRoutePlan(self):
        try:
            result = self.db.outlet_activity.find({"date":{"$gte":self.startDate,"$lte":self.endDate} })
            self.routePlans = defaultdict(lambda: defaultdict(list))
            for row in result:
                d = row['date']
                timestamp,check_in,check_out,start,end = self.getActivity(row['checkin_activity'])
                #print(timestamp,check_in,check_out)
                self.routePlans[d.strftime("%d-%b")][str(row['fwp_id'])] = (timestamp,check_in,check_out,start,end)
                
                #print(self.routePlans[d.strftime("%d-%b")][str(row['fwp_id'])])
        except Exception as e:
            print("getRoutePlan Error : " + str(e))
            #return ''
                
            
    def attendanceReport(self,req):
        ttt = None
        try:
            date = req['filter']['date']
            self.dates = self.getDays(date)  
            
            self.getRoutePlan()
            
            aggr = [{"$lookup": { "from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"}]
            aggr.append({"$match":{"date":{"$gte":self.startDate,"$lte":self.endDate} } })
            
            result = self.db.attendance.aggregate(aggr,allowDiskUse=True)
            
            self.cities = defaultdict(lambda: defaultdict(list))            
            data = {}
            
            for row in result:
                ttt = row
                #print(row)
                t = {}
                id = str(row['user']['_id'])
                
                if id in data:
                    t = data[str(row['user']['_id'])] 
                    try:
                        t['WORKING HOURS'] = t['WORKING HOURS'] + row['duration']
                    except:
                        print(t['WORKING HOURS'])
                else:
                    t = copy.deepcopy(self.row) 
                    #print(row['user']['name'])
                    #t['SR.NO'] = c
                    t['FWP NAME'] = row['user']['name']
                    t['CITY'] = self.city[str(row['user']['city_id'])]
                    t['DESIGNATION'] = self.roles[row['user']['role']]
                    t['EMP CODE'] = row['user']['code']
                    t['ROLE'] = row['user']['role']
                    t['TOTAL'] = '0'
                    t['DOJ'] = ''
                    t['WORKING STATUS'] = 'Working'
                    t['WORKING HOURS'] = row['duration']
                
                
                if 'error_level' in row:
                    if row['error_level'] > 5:    
                        t[row['date'].strftime("%d-%b")] = 0.5
                    else:
                        t[row['date'].strftime("%d-%b")] = 1
                else:
                    t[row['date'].strftime("%d-%b")] = 1
                
                if row['user']['role'] == 2:
                    if 'supervisor_checkin_activity' in row:
                        timestamp,check_in,check_out,start,end = self.getActivity(row['supervisor_checkin_activity'])
                        t[row['date'].strftime("%d-Timestamp")] = timestamp
                        t[row['date'].strftime("%d-Coordinates")] = check_in+' / '+check_out
                        t[row['date'].strftime("%d-Check-In")] = start
                        t[row['date'].strftime("%d-Check-Out")] = end
                        t[row['date'].strftime("%d-Working Hrs")] = round((row['duration'] / 60) / 60)
                try:
                    timestamp,check_in,check_out,start,end = self.routePlans[row['date'].strftime("%d-%b")][str(row['user_id'])]
                
                #print(coardinates)
                    #t[row['date'].strftime("%d-%b")] = timestamp
                    # ~ t[row['date'].strftime("%d-%b-Timestamp")] = timestamp
                    t[row['date'].strftime("%d-Timestamp")] = timestamp
                    t[row['date'].strftime("%d-Coordinates")] = check_in+' / '+check_out
                    # ~ t[row['date'].strftime("%d-%b-Check-In")] = check_in
                    # ~ t[row['date'].strftime("%d-%b-Check-Out")] = check_out
                    t[row['date'].strftime("%d-Check-In")] = start
                    t[row['date'].strftime("%d-Check-Out")] = end
                    t[row['date'].strftime("%d-Working Hrs")] = round((row['duration'] / 60) / 60)
                except Exception as e:
                    print("OutletActivity Set : "+str(e))
                
                data[id] = t
                #self.city[t['CITY']][id].append(t)
                #print(self.city)
                #exit()
                
            for k in data:
                t = data[k]   
                role = t['ROLE']
                del t['ROLE']
                self.cities[t['CITY']][role].append(t)      
            
            
            id = ObjectId()
            #print(date)
            month = date.strftime("%b")
            #print(month)
            name = 'Attandance-'+month+"-"+str(id)+'.xlsx'
            
            #name = 'Attandance - Oct.xlsx'
            filename = self.path+name
            
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("SUMMARY")
            
            #writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            
            # Write each dataframe to a different worksheet.
            
            for k in self.cities: 
                
                row = self.cities[k]
                
                c = 0
                worksheet1 = workbook.add_worksheet(k)
                worksheet1.set_column(0, 4, 17)
                
                if 3 in row:
                    row1 = row[3]
                    bg_clr = '#999966'
                    bg_txt_clr = '#d6d6c2'
                    c = self.__insertWorksheet(c, "CITY MANAGER ATTENDANCE", workbook, worksheet1, row1, bg_clr, bg_txt_clr, date)
                
                if 2 in row:
                    row1 = row[2]
                    bg_clr = '#9900cc'
                    bg_txt_clr = '#ccccff'
                    c = self.__insertWorksheet(c, "SUPERVISORS ATTENDANCE", workbook, worksheet1, row1, bg_clr, bg_txt_clr, date) 
                    
                if 1 in row:
                    row1 = row[1]
                    bg_clr = '#009999'
                    bg_txt_clr = '#00cccc'
                    c = self.__insertWorksheet(c, "FWPs ATTENDANCE", workbook, worksheet1, row1, bg_clr, bg_txt_clr, date) 
               
                
               
            workbook.close()
           
            self.db.report_requests.update_one({'_id':req['_id']},{"$set":{'status':3,'filename':name}})
            
        except Exception as e:
            print("Error : " + str(e),row)
     
     
     
            
    def start(self):
        try:
            result = self.db.report_requests.find({'status':0})
            #result = self.db.report_requests.find()
            reports = []
            for row in result:
                reports.append(row)
            
            for row in reports:
                #print(row)
                if row['name'] == "Attendance":
                    self.db.report_requests.update_one({'_id':row['_id']},{"$set":{'status':1}})
                    self.attendanceReport(row)
                    
               
        except Exception as e:
            print(e)
                
o = Attendance()
o.start()

#print("Start.....")
#o.activeOutletReport()
print("Completed.....")







