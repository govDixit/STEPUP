from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,requestJsonData, getRow
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from bson import ObjectId
import xlsxwriter
from datetime import datetime

@apiV1.resource('/broadcast/<id>')
class Broadcast(Resource):
    
    def __init__(self):
        self.update_fields = {'areas': {'type': 'string','required': True,'empty': True},
                              'status': {'type': 'number','required': True,'allowed': [0, 1]}}
        
    def get(self,id):
        result = mongo.db.broadcast_questions.find_one_or_404({"_id":getId(id)})
        return getData(result),200
    
   
                     
@apiV1.resource('/broadcast')
class BroadcastList(Resource):
    
    def __init__(self):
        self.create_fields = {'user_id': {'type': 'string','required': True,'empty': False},
                              'name': {'type': 'string','required': True,'empty': False},
                              'option1': {'type': 'string','required': True,'empty': False},
                              'option2': {'type': 'string','required': True,'empty': False},
                              'option3': {'type': 'string','required': True,'empty': False},
                              'option4': {'type': 'string','required': True,'empty': False},
                              'type': {'type': 'string','required': True,'allowed': ['radio', 'checkbox']},
                              'answers': {'type': 'list','required': True,'empty': False}}
        
    def get(self):
        try:
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            
            self.user = getCurrentUser() 
            # City Manager Filter
            if self.user['role'] == 3:
                data = {"draw":0,"recordsTotal":0,"recordsFiltered":0,"data":[]}
                return data,200
            
            if search != '':
                result = mongo.db.broadcast_questions.find({'name':{'$regex' : search, '$options' : 'i'}}).skip(start).limit(length).sort([('_id', -1)])
            else:
                result = mongo.db.broadcast_questions.find().skip(start).limit(length).sort([('_id', -1)])
                
            total = result.count()
            
            list  = []
            for row in result:
                row['created_at'] = row['created_at'].strftime("%d %b, %Y %I:%M:%S %p")
                list.append(getRow(row))
            
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = list
            return data,200
        except:
            return {'error':{"message":"Something Wrong"}},400
    
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            #return json,200
            if v.validate(json):
                json['test_type'] = "broadcast";
                json['lang_id'] = None
                json['user_id'] = getId(json['user_id'])
                
                json['priority'] = int(0)
                json['read'] = int(0)
                json['status'] = int(1)
                json['created_at'] = datetime.now()
                
                id = mongo.db.broadcast_questions.insert(json)
                #print(id)
                self.insertFwp(json['user_id'], id)
                
                return {'status':'ok','id':str(id)},201
            else:
                return {'error':v.errors},400
        except:
            return {'error':{"message":["City already exist."]}},400
           
    
    
    def insertFwp(self,supervisor_id,broadcast_questions_id):
        try:
            json = {}
            json['broadcast_questions_id'] = broadcast_questions_id
            json['user_id'] = supervisor_id
            json['priority'] = int(0)
            json['answers'] = []
            json['read'] = int(0)
            json['status'] = int(1)
            json['answered_at'] = None
            json['created_at'] = datetime.now()
            
            mongo.db.broadcast_users.insert(json)
                
            result = mongo.db.users.find({'parent_id':supervisor_id})
            fwps = []
            for row in result:
                json = {}
                json['broadcast_questions_id'] = broadcast_questions_id
                json['user_id'] = row['_id']
                json['priority'] = int(0)
                json['answers'] = []
                json['read'] = int(0)
                json['status'] = int(1)
                json['answered_at'] = None
                json['created_at'] = datetime.now()
                mongo.db.broadcast_users.insert(json)
        except Exception as e:
            print(e)
            return {'error':{"message": str(e)}},400
 

@apiV1.resource('/broadcast/result/<id>')
class BroadcastResult(Resource):
    
    def get(self,id):
        try:
            result = mongo.db.broadcast_users.find({'broadcast_questions_id':getId(id)})
            
            aggr = [{"$lookup": { "from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"}]
            aggr.append({"$match":{"broadcast_questions_id":getId(id)}})
            
            result = mongo.db.broadcast_users.aggregate(aggr)
            
            question = mongo.db.broadcast_questions.find_one({"_id":getId(id)})
            
            q = {'name':'','type':'','options':''}
            answer = ''
            if question:
                q['name'] = question['name']
                q['type'] = question['type']
                q['options'] = question['option1'] + ", " + question['option2'] + ", " + question['option3'] + ", " + question['option4']
                answer = ', '.join([str(question[elem]) for elem in question['answers']])
                
            
            data = []
            for row in result:
                t = {}
                ans = ', '.join([str(elem) for elem in row['answers']])
                
                t['question'] = q['name']
                t['type'] = q['type']
                t['options'] = q['options']
                t['answers'] = answer
                t['user'] = row['user']['name']
                t['user_answers'] = ans
                #print(answer+" : "+ans)
                if answer == ans:
                    t['result'] = "Correct"
                else:
                    t['result'] = "InCorrect"
                    
                t['read'] = row['read']
                
                if row['answered_at'] != None:
                    t['answered_at'] = row['answered_at'].strftime("%d %b, %Y %I:%M:%S %p")
                else:
                    t['answered_at'] = '--'
                    
                t['created_at'] = row['created_at'].strftime("%d %b, %Y %I:%M:%S %p")
                
                data.append(t)
                
            return data,200
        
        except Exception as e:
            return {'error':{"message": str(e)}},400
        
    def getUser(self,user_id):
        user = mongo.db.users.find_one({"_id":getId(user_id)})
        if user:
            return user['name'] + " - " + user['code']
        
        
        
    def post(self,id):
        try:
            data,code = self.get(id)
            #print(data)
            #exit()
            
            # Create a workbook and add a worksheet.
            self.path = app.config['UPLOAD_FOLDER']+"reports/"
            
            id = ObjectId()
            name = 'Broadcast-Result-'+str(id)+'.xlsx'
            filename = self.path+name   
            
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("Broadcast Result")
            
            c = 0
            c = self.__insertWorksheet(c,'Result',workbook,worksheet,data)
            
            worksheet.set_column(0, 1, 7)
            worksheet.set_column(1, 2, 25)
            worksheet.set_column(2, 7, 16)
            workbook.close()
            
            path = "../"+app.config['UPLOAD_FOLDER']+'reports/'+name
            return send_file(path, as_attachment=True)
            # ~ return {'status':'Ok','filename':name},200
        
        except Exception as e:
            return {'error':{"message":"Error " + str(e)}},400
        
        
        
    
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
        
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        header_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'align':'center','valign':'vcenter','bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'align':'center','valign':'vcenter','bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        
       
        worksheet.write(c,0,'Sr.No.',header_format)
        worksheet.write(c,1,'QUESTION',header_format)
        worksheet.write(c,2,'OPTIONS',header_format)
        worksheet.write(c,3,'ANSWERS',header_format)
        worksheet.write(c,4,'USER',header_format)
        worksheet.write(c,5,'USER ANSWERS',header_format)
        worksheet.write(c,6,'RESULT',header_format)
        worksheet.write(c,7,'ANSWER AT',header_format)
        
        for row in data:
            c += 1
            #print(row)
            #print("\n")
            self.__insertRow(worksheet,c,row,format1,format2)
        return c+2
        
            
    def __insertRow(self,worksheet,c,row,format1,format2):   
        if (c % 2) == 0:  
            worksheet.set_row(c, cell_format=format1)
        else:
            worksheet.set_row(c, cell_format=format2) 
        
        #print(row)
        worksheet.write(c,0,c)
        worksheet.write(c,1,row['question'])
        worksheet.write(c,2,row['options'].replace(",","\n"))
        worksheet.write(c,3,row['answers'].replace(",","\n"))
        worksheet.write(c,4,row['user'])
        worksheet.write(c,5,row['user_answers'].replace(",","\n"))
        worksheet.write(c,6,row['result'].replace(",","\n"))
        worksheet.write(c,7,row['answered_at'])
        
        
        
        
        
        
        
        
        
        
        

 
@apiV1.resource('/broadcast/export')
class BroadcastExport(Resource):
    def __init__(self):
        self.roles = {1:'FWP',2:'SUPERVISOR',3:'CITY MANAGER',4:'IPM'}
        
        
    def post(self):
        try:
            json = request.get_json()
            query = {}
            
            result = mongo.db.broadcast_questions.find(query)
            data = list(result)
            
            # Create a workbook and add a worksheet.
            self.path = app.config['UPLOAD_FOLDER']+"reports/"
            
            id = ObjectId()
            name = 'Broadcast-'+str(id)+'.xlsx'
            filename = self.path+name   
            
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("Broadcast")
            
            c = 0
            c = self.__insertWorksheet(c,'Questions',workbook,worksheet,data)
            
            
            worksheet.set_column(0, 4, 25)
            workbook.close()

            path = "../"+app.config['UPLOAD_FOLDER']+'reports/'+name
            return send_file(path, as_attachment=True)
            # ~ return {'status':'Ok','filename':name},200
            
        
        except Exception as e:
            return {'error':{"message":"Error " + str(e)}},400    

    
        
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
        
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        header_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'align':'center','valign':'vcenter','bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'align':'center','valign':'vcenter','bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        
        
        #worksheet.merge_range('B'+str(c+1)+':E'+str(c+1),title,tittle_format)   
        
        #c += 1    
        
        worksheet.write(c,0,'Sr.No.',header_format)
        worksheet.write(c,1,'QUESTION',header_format)
        worksheet.write(c,2,'OPTIONS',header_format)
        worksheet.write(c,3,'ANSWER',header_format)
        
        for row in data:
            c += 1
            self.__insertRow(worksheet,c,row,format1,format2)
        return c+2
        
            
    def __insertRow(self,worksheet,c,row,format1,format2):   
        if (c % 2) == 0:  
            worksheet.set_row(c, cell_format=format1)
        else:
            worksheet.set_row(c, cell_format=format2) 
        
        worksheet.write(c,0,c)
        worksheet.write(c,1,row['name'])
        worksheet.write(c,2,row['option1']+"\n"+row['option2']+"\n"+row['option3']+"\n"+row['option4'])
        worksheet.write(c,3,"\n".join(row['answers']))
        
        
