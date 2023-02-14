from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUserId, dateTimeValidate
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
import pandas as pd
import uuid,os
import xlsxwriter


@apiV1.resource('/report/download/<filename>')
class ReportDownload(Resource):
    def get(self,filename):
        try:
            path = "../"+app.config['UPLOAD_FOLDER']+'reports/'+filename
            return send_file(path, as_attachment=True)
        except:
            return {'error':{"message":"Something Wrong."}},400
 


@apiV1.resource('/report/activeOutlet')
class ReportActiveOutlet(Resource):
    
    def __init__(self):
        self.create_fields = {'city_id': {'required': True,'empty': False},
                              'fromDate': {'required': True,'empty': False}}
        
        
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=True)
            json = request.get_json()
           
            if v.validate(json):
                self.dateInput = datetime.strptime(json['fromDate'],"%Y-%m-%d")
                json['fromDate'] = self.dateInput
                
                city_id = getId(json['city_id'])
                if city_id == False:
                    city_id = None
                
                data = {}
                data['name'] = "ActiveOutlets"
                data['filter'] = {'city_id':city_id,'date':self.dateInput}
                data['status'] = 0
                data['filename'] = ''
                data['created_at'] = datetime.now()
                
                mongo.db.report_requests.insert(data)
                
                return {'status':'Ok'},201
            else:
                return {'error':v.errors},400
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400
            
            
            
            
    def _getUser(self,id):
        result = mongo.db.users.find_one({'_id':id})
        user = {}
        user['name'] = ''
        user['code'] = ''
        if result:
            user['name'] = result['name']
            user['code'] = result['code']
        return user
    
    def post1(self):
        try:
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            json = request.get_json()
            self.dateInput = datetime.strptime(json['fromDate'],"%Y-%m-%d")
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            aggr.append({"$match":{"date":self.dateInput}})
            
            result = mongo.db.outlet_activity.aggregate(aggr)
            
            data = []
            t = {}
            t['srno'] = 'SR.NO'
            t['date'] = 'DATE'
            t['day'] = 'DAY'
            t['time'] = 'TIME'
            t['outlet_code'] = 'OUTLET CODE'
            t['outlet_name'] = 'OUTLET NAME'
            t['address'] = 'OUTLET ADDRESS'
            t['fwp_name'] = 'FWP NAME'
            t['fwp_code'] = 'FWP CODE'
            t['active'] = 'ACTIVE'
            t['zone'] = 'ZONE'
            t['contact'] = 'CONTACT'
            t['tse'] = 'TSE'
            t['asm'] = 'ASM'
            t['meeting'] = 'MEETING'
            t['activity'] = 'ACTIVITY'
            t['cycle'] = 'CYCLE'
            #data.append(t)
            
            columns = ['SR.NO','DATE','DAY','TIME','OUTLET CODE','OUTLET NAME','OUTLET ADDRESS','FWP NAME','FWP CODE','ACTIVE','ZONE','CONTACT','TSE','ASM','MEETING','ACTIVITY','CYCLE']
            
            temp = []
            c = 0
            if result:   
                for row in result:
                    c = c+1
                    user = self._getUser(getId(row['fwp_id']))
                    
                    t = {}
                    t['SR.NO'] =  c
                    t['DATE'] = str(row['date']).replace(" 00:00:00", "")
                    t['DAY'] =  row['date'].strftime('%A')
                    t['TIME'] = str(row['start_time'])+' - '+str(row['end_time'])
                    t['OUTLET CODE'] = row['outlet']['code']
                    t['OUTLET NAME'] = row['outlet']['name']
                    t['OUTLET ADDRESS'] = row['outlet']['address']
                    t['FWP NAME'] = user['name']
                    t['FWP CODE'] = user['code']
                    t['ACTIVE'] = 'YES'
                    t['ZONE'] = row['outlet']['zone']
                    t['CONTACT'] = row['contact']
                    t['TSE'] = row['tse']
                    t['ASM'] = row['asm']
                    t['MEETING'] = row['meeting']
                    t['ACTIVITY'] = row['activity']
                    t['CYCLE'] = row['cycle']
                    data.append(t)
                    
                
                # Create a Pandas dataframe from some data.
                
                df = pd.DataFrame(data,columns=columns)
                df.reset_index(drop=True, inplace=True)
                
                #print(df)
                
                #df = pd.DataFrame(data)
                name = 'ActiveOutlets-'+str(uuid.uuid4())+'.xlsx'
                filename = os.path.join(app.config['UPLOAD_FOLDER']+'/reports/'+name)
               
                writer = pd.ExcelWriter(filename, engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Outlet',index=False)
               

                #Close the Pandas Excel writer and output the Excel file.
                writer.save()
                filename = app.config['REPORT_URL']+name
                
                return {'status':'Ok','filename':filename},200
            else:
                return {'error':{"message":"Outlet is not found"}},404
                
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong."}},400
        
    