from api import app, mongo, apiV1
from flask import request,send_file
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity
from api.lib.helper import getData,getId,getRow,getCurrentUser,check_permissions
from cerberus import Validator
from bson import ObjectId
from pymongo.errors import DuplicateKeyError 
import hashlib 
import json
import os
import base64
import pandas as pd
from io import StringIO
from bson import ObjectId
import xlsxwriter
from collections import defaultdict
from os import path
from datetime import timedelta, date,datetime
import re

"""class CustomErrorHandler(errors.BasicErrorHandler):
    messages = errors.BasicErrorHandler.messages.copy()
    messages[errors.MAX_VALUE.code] = 'Status value is not a Valid!'"""


def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """

    # calculating the length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"[ !#@$%&'()*+,-./[\\\]^_`{|}~"+r'"]', password) is None

    # overall result
    password_ok = not ( length_error or digit_error or uppercase_error or lowercase_error or symbol_error )
    
    if password_ok:
        return {"status":"OK"}
    
    error = None
    if length_error:
        error = "Your password must be at least 8 characters."
    elif digit_error:
        error = "Your password must have at least 1 number."
    elif uppercase_error or lowercase_error:
        error = "Your password must have at least 1 lower case and upper case character."
    elif symbol_error:
        error = "Your password must have at least 1 special character."
    
    if error is not None:
        return {'error':{"message":error}}
    
    
@apiV1.resource('/user/<id>')
class User(Resource):
    
    def __init__(self):
        self.update_fields = {'name': {'type': 'string','empty': False},
                              'code': {'type': 'string','empty': False},
                              'email': {'type': 'string','empty': False},
                              #'mobile': {'type': 'number','empty': False,'minlength':10,'maxlength':10},
                              'password': {'type': 'string','minlength':6,'maxlength':16},
                              'confirmPassword': {'type': 'string','minlength':6,'maxlength':16},
                              'status': {'type':'number','allowed': [0, 1]},
                              'isLocked': {'type':'number','allowed': [0, 1]},
                              'parent_id': {'type': 'string'},
                              'city_id': {'type': 'string'},
                              'role': {'type':'number','allowed': [1,2,3,4,5]}}
        
    def get(self,id):
        try:
            user = mongo.db.users.find_one({"_id":getId(id)})
            if user:
                user.pop('password')
                #if user['parent_id']
                return getData(user),200
            else:
                return {'error':{"message":"User is not found."}},404
        except:
            return {'error':{"message":"Something Wrong"}},400
    
    def put(self,id):
        v = Validator(self.update_fields,allow_unknown=False)
        json = request.get_json()
        if v.validate(json):
            if 'password' in json: 
                if json['password'] != json['confirmPassword']:
                    return {'error': {"confirmPassword": ["Password and Confirm Password are not matching."]}}, 400
                del json['confirmPassword']
                
                #Password policy check
                pr = password_check(json['password'])
                if 'error' in pr:
                    return pr,400
                
                json['password'] =  hashlib.md5(json['password'].encode()).hexdigest()
                
                
            
            #json['profile_pic'] = 'user.png'
            
            if 'parent_id' in json: 
                json['parent_id'] = getId(json['parent_id'])
                
                #if not json['parent_id']:
                if json['role'] == 1 and json['parent_id'] == False:
                    return {'error':{"supervisor":"Supervisor is missing or not valid.","city_manager":"City Manager is missing or not valid."}},400
                elif json['role'] == 2 and json['parent_id'] == False:
                    return {'error':{"city_manager":"City Manager is missing or not valid."}},400
                if json['parent_id'] == False:
                    json['parent_id'] = None
            
            if 'city_id' in json:         
                json['city_id'] = getId(json['city_id'])
                    
            user = mongo.db.users.find_one_or_404({"_id":getId(id)})
            
            myquery = {"_id":getId(id)}
            newvalues = {"$set": json}
            
            mongo.db.users.update_one(myquery, newvalues)
            
            user = mongo.db.users.find_one_or_404({"_id":getId(id)})
            return getData(user),200
        else:
            return {'error':v.errors},400
        
    def delete(self,id):
        
        user = mongo.db.users.find_one_or_404({"_id":getId(id)})
        
        myquery = {"_id":getId(id)}
        newvalues = {"$set": {"status":3}}
        
        mongo.db.users.update_one(myquery, newvalues)
        
        return {'status':'ok'},202
           
           
           
@apiV1.resource('/user')
class UserList(Resource):
    
    def __init__(self):
        self.create_fields = {'name': {'type': 'string','required': True,'empty': False},
                              'code': {'type': 'string','required': True,'empty': False},
                              'email': {'type': 'string','required': True,'empty': False},
                              'mobile': {'type': 'number','required': True,'empty': False,'minlength':10,'maxlength':10},
                              'password': {'type': 'string','required': True,'empty': False,'minlength':6,'maxlength':16},
                              'confirmPassword': {'type': 'string','required': True,'empty': False,'minlength':6,'maxlength':16},
                              'status': {'type':'number','required': True,'allowed': [0, 1]},
                              'isLocked': {'type':'number','allowed': [0, 1]},
                              'parent_id': {'required': True},
                              'city_id': {'type': 'string'},
                              'role': {'type':'number','required': True,'allowed': [1,2,3,4,5]}}
        
        self.user = getCurrentUser() 
        
            
    def get(self):
        try:
            
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search','')
            role = int(request.args.get('role',4))
            parent_id = request.args.get('parent_id',0)
            
            query = {}
            if parent_id != 0:
                query['parent_id'] = getId(parent_id)
            if search != '':
                query['$or'] = [{'name':{'$regex' : search, '$options' : 'i'}},{'code':search}]
                
            query['role'] = role  
            
            # City Manager Filter
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])
                
                if role > 3:
                    data = {"draw":0,"recordsTotal":0,"recordsFiltered":0,"data":[]}
                    return data,200
           
                
            #for city manager login
            if self.user['role'] < 3:
                data = {"draw":0,"recordsTotal":0,"recordsFiltered":0,"data":[]}
                return data,200
            
            
            user_results = mongo.db.users.find(query).skip(start).limit(length).sort([('status', -1)])
                
            total = user_results.count()
            
            users = []
            parent_ids = []
            parent_users = {}
            for row in user_results:
                if row['parent_id'] != None:
                    parent_ids.append(row['parent_id'])
                users.append(getRow(row))
            
            
            #Fetch parent names   
            if len(parent_ids) > 0: 
                result = mongo.db.users.find({"_id": {"$in": parent_ids}})
                for row in result:
                    parent_users[str(row['_id'])] = row['name']
            
           
            for row in users:
                try:
                    if row['parent_id'] != None:
                        row['parent_name'] = parent_users[str(row['parent_id'])]
                    else:
                        row['parent_name'] = 'None'
                except:
                    row['parent_name'] = 'None'   
                
            
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = users
            return data,200
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400
           
    def post(self):
        try:
            v = Validator(self.create_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                
                
                expiry_date = date.today() + timedelta(days=90)
                expiry_date = datetime.strptime(str(expiry_date),"%Y-%m-%d")
                
                #for city manager login
                if self.user['role'] == 3 and json['role'] > 2:
                    return {'error':{"message":"You can't add user in IPM and City Manager"}},400
                
                #Password policy check
                pr = password_check(json['password'])
                if 'error' in pr:
                    return pr,400
                
                
                if json['password'] != json['confirmPassword']:
                    return {'error': {"confirmPassword": ["Password and Confirm Password are not matching."]}}, 400
                
                del json['confirmPassword']
                json['profile_pic'] = 'user.png'
                json['parent_id'] = getId(json['parent_id'])
                json['city_id'] = getId(json['city_id'])
                
                json['deviceId'] = None
                json['firebaseToken'] = None
                json['rating'] = 0
                json['isLocked'] = 0
                json['expiry_date'] = expiry_date
                json['created_at'] = datetime.now()
                
                
                #if not json['parent_id']:
                if json['role'] == 1 and json['parent_id'] == False:
                    return {'error':{"supervisor":"Supervisor is missing or not valid.","city_manager":"City Manager is missing or not valid."}},400
                elif json['role'] == 2 and json['parent_id'] == False:
                    return {'error':{"city_manager":"City Manager is missing or not valid."}},400
                if json['parent_id'] == False:
                    json['parent_id'] = None
                    
                #print(json);
                json['password'] =  hashlib.md5(json['password'].encode()).hexdigest()
                id = mongo.db.users.insert(json)
                return {'status':'ok','id':str(id)},201
            else:
                return {'error': v.errors}, 400
        except DuplicateKeyError:
            return {'error':{"message":"User already exist."}},400
 


    
@apiV1.resource('/user/select')
class UserSelect(Resource): 
    def get(self):
        try:
            self.user = getCurrentUser() 
            query = {}
            # City Manager Filter
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])
                
            query['role'] = 3
          
            users = mongo.db.users.find(query)
            user_ids = []
            users_dict = {}
            data = {}
                    
            for row in users:
                data[str(row['_id'])] = {'id':str(row['_id']),'name':row['name'],'supervisor':[]}
                user_ids.append(getId(row['_id']))   
                
            result = mongo.db.users.find({"parent_id": {"$in": user_ids}}) 
            for row in result:
                data[str(row['parent_id'])]['supervisor'].append({'id':str(row['_id']),'name':row['name']})
            
            
            """aggr = [{"$lookup": { "from": "users", "localField": "parent_id", "foreignField": "_id", "as": "parent"}},{ "$unwind": "$parent"}]
            aggr.append({"$match":{"role":2}})
            
            
            aggr = [{"$lookup": { "from": "users", "localField": "_id", "foreignField": "parent_id", "as": "supervisor"}},{ "$unwind": "$supervisor","preserveNullAndEmptyArrays": "true"}]
            aggr.append({"$match":{"role":3}})
            
            users = mongo.db.users.aggregate(aggr)
            data = {}
            temp = []
            
            for row in users:
                supervisor = row['supervisor']
                
                if str(row['_id']) in data:
                    data[str(row['_id'])]['supervisor'].append({'id':str(supervisor['_id']),'name':supervisor['name']})
                else:
                    data[str(row['_id'])] = {'id':str(row['_id']),'name':row['name'],'supervisor':[]}
                    data[str(row['_id'])]['supervisor'].append({'id':str(supervisor['_id']),'name':supervisor['name']})"""
              
            temp = []
            for key in data:
                temp.append(data[key])
                
            return temp,200
        except Exception as e:
            print(e)
            return [],200
        
@apiV1.resource('/user/select/<id>')
class UserSelectByParent(Resource): 
    def get(self,id):
        try:
            users = mongo.db.users.find({'parent_id':getId(id)})
           
            data = []
            
            for row in users:
                data.append({'id':str(row['_id']),'name':str(row['name'])})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200
 
@apiV1.resource('/user/selectbycity/<id>')
class UserSelectByCity(Resource): 
    def get(self,id):
        try:
            users = mongo.db.users.find({'city_id':getId(id),'role':2})
           
            data = []
            
            for row in users:
                data.append({'id':str(row['_id']),'name':row['name']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200
        
                   
@apiV1.resource('/user/child/<parent_id>')
class UserListByParent(Resource):
    decorators = [check_permissions]
    
    def get(self,parent_id):
        try:
            r = range(1, 5)
            users = []
            
            if getId(parent_id):
                result = mongo.db.users.find({'parent_id':getId(parent_id)})
                
                for row in result:
                    t = {}
                    t['id'] = str(row['_id'])
                    t['code'] = row['code']
                    t['mobile'] = row['mobile']
                    t['name'] = row['name']
                    t['profile_pic'] = row['profile_pic']
                    t['parent_id'] = str(row['parent_id'])
                    t['role'] = row['role']
                    t['city_id'] = str(row['city_id'])
                    t['rating'] = row['rating']
                    users.append(t)
                    
            elif int(parent_id) in r:
                result = mongo.db.users.find({'role':int(parent_id)})
                
                for row in result:
                    t = {}
                    t['id'] = str(row['_id'])
                    t['code'] = row['code']
                    t['mobile'] = row['mobile']
                    t['name'] = row['name']
                    t['profile_pic'] = row['profile_pic']
                    t['parent_id'] = str(row['parent_id'])
                    t['role'] = row['role']
                    t['city_id'] = str(row['city_id'])
                    t['rating'] = row['rating']
                    users.append(t)
           
            return users,200
        except Exception as e:
            return {'error':{"message":"Something Wrong "+str(e)}},400
    
   
    
@apiV1.resource('/profile')
class UserProfile(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.update_fields = {'password': {'type': 'string','minlength':6,'maxlength':16},
                              'confirmPassword': {'type': 'string','minlength':6,'maxlength':16},
                              'profile_pic': {'type': 'string'}  }
    
    def get(self):
        profile_id = get_jwt_identity()
        user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})

        user.pop('password') 
        return {'profile': getData(user)},200
    
    def put(self):
        profile_id = get_jwt_identity()
        
        try:
            v = Validator(self.update_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                if 'password' in json: 
                    if json['password'] != json['confirmPassword']:
                        return {'error': {"confirmPassword": ["Password and Confirm Password are not matching."]}}, 400
                    del json['confirmPassword']
                    
                    #Password policy check
                    pr = password_check(json['password'])
                    if 'error' in pr:
                        return pr,400
                
                    json['password'] =  hashlib.md5(json['password'].encode()).hexdigest()
                    
                if 'profile_pic' in json:
                    profile_pic = json['profile_pic']
                    filename = os.path.join(app.config['UPLOAD_FOLDER']+"profile/", str(profile_id)+".jpg")
                    
                    self.base64ToImage(profile_pic, filename)
                    json['profile_pic'] = filename
                    
                    
                        
                user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})
                
                myquery = {"_id":getId(profile_id)}
                newvalues = {"$set": json}
                
                mongo.db.users.update_one(myquery, newvalues)
                
                user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})
                user.pop('password')
                return {'profile': getData(user)},200
            else:
                return {'error':v.errors},400
        except Exception as e:
            return {'error':{"message":"Something Wrong "+str(e)}},400
    
    
    def base64ToImage(self, data, filename):
        imgdata = base64.b64decode(data)
        with open(filename, 'wb') as f:
            f.write(imgdata)




@apiV1.resource('/passwordReset')
class UserPasswordReset(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.update_fields = {
                              'current_password': {'type': 'string','minlength':6,'maxlength':16,'required': True,'empty':False},
                              'password': {'type': 'string','minlength':6,'maxlength':16,'required': True,'empty':False},
                              'confirmPassword': {'type': 'string','minlength':6,'maxlength':16,'required': True,'empty':False}}
    
    
    def put(self):
        profile_id = get_jwt_identity()
        
        try:
            user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})
            
            v = Validator(self.update_fields,allow_unknown=False)
            json = request.get_json()
            if v.validate(json):
                
                if user['password'] != hashlib.md5(json['current_password'].encode()).hexdigest():
                    return {'error': {"message":"Your current password is not a valid"}}, 400
                
               
                if json['password'] != json['confirmPassword']:
                    return {'error': {"message": "Password and Confirm Password are not matching."}}, 400
                
                #Password policy check
                pr = password_check(json['password'])
                if 'error' in pr:
                    return pr,400
                
                new_password =  hashlib.md5(json['password'].encode()).hexdigest()
                
                        
                user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})
                
                expiry_date = date.today() + timedelta(days=90)
                expiry_date = datetime.strptime(str(expiry_date),"%Y-%m-%d")
                
                myquery = {"_id":getId(profile_id)}
                newvalues = {"$set": {'password':new_password,'expiry_date':expiry_date}}
                
                mongo.db.users.update_one(myquery, newvalues)
                
                user = mongo.db.users.find_one_or_404({"_id":getId(profile_id)})
                user.pop('password')
                return {'profile': getData(user)},200
            else:
                return {'error':v.errors},400
        except Exception as e:
            return {'error':{"message":"Something Wrong "+str(e)}},400
    
    


@apiV1.resource('/user/pic/<filename>')
class UserPic(Resource):
    decorators = [check_permissions]
    
    def get(self,filename):
        try:
            file = "../"+app.config['UPLOAD_FOLDER']+'profile/'+filename
            
            return send_file(file, as_attachment=True)
        except:
            return {'error':{"message":"Something Wrong."}},400   



@apiV1.resource('/user/import')
class UserImport(Resource):
    
    def post(self):
        try:
            json = request.get_json()
            city_id = getId(json['city_id'])
            users = json['user']
            users = users.split(',')[1]
            role = json['role']
            #users = users.replace("data:text/csv;base64", "")
            
            parent_id = getId(json['parent_id'])
            
            #if not json['parent_id']:
            if json['role'] == 1 and parent_id == False:
                return {'error':{"supervisor":"Supervisor is missing or not valid.","city_manager":"City Manager is missing or not valid."}},400
            elif json['role'] == 2 and parent_id == False:
                return {'error':{"city_manager":"City Manager is missing or not valid."}},400
            if parent_id == False:
                parent_id = None;
                
            
            #print(outlets)
            
            code_string = base64.b64decode(users)
            #code_string = code_string.decode('utf-8')
            code_string = code_string.decode('utf-8',errors="ignore")
            TESTDATA = StringIO(code_string)
            df = pd.read_csv(TESTDATA, sep=",")
            
            #print(df)
            
            expiry_date = date.today() + timedelta(days=90)
            expiry_date = datetime.strptime(str(expiry_date),"%Y-%m-%d")
         
            #return {'status':'ok'},201
            for index, row in df.iterrows():
                password = str(row['password'])
                t = {}
                t['city_id'] = city_id
                t['name'] = row['name']
                t['code'] = row['code']
                t['email'] = row['email']
                t['mobile'] = row['mobile']
                t['password'] = hashlib.md5(password.encode()).hexdigest()
                t['status'] = 1
                t['role'] = role
                t['parent_id'] = parent_id
                t['profile_pic'] = "user.png"
                t['deviceId'] = None
                t['firebaseToken'] = None
                t['rating'] = 0
                t['isLocked'] = 0
                t['expiry_date'] = expiry_date
                t['created_at'] = datetime.now()
                
                mongo.db.users.insert(t)
             
            return {'status':'ok'},201
        
        except DuplicateKeyError:
            return {'error':{"message":["User already exist."]}},400
        except Exception as e:
            print(e)
            return {'error':{"message":["Something wrong."]}},400
            
 
 
 
@apiV1.resource('/user/export')
class UserExport(Resource):
    def __init__(self):
        self.roles = {1:'FWP',2:'SUPERVISOR',3:'CITY MANAGER',4:'IPM'}
        
        result = mongo.db.city.find()
        self.cities = {}
        for row in result:
            self.cities[str(row['_id'])] = row['name']
        
        
    def post(self):
        try:
            json = request.get_json()
            query = {}
            
            json['parent_id'] = getId(json['parent_id'])
     
            if json['parent_id'] != False:
                query['parent_id'] = json['parent_id']
                
            #query['role'] = json['role']
            
            
           
            
            result = mongo.db.users.find(query)
            #print(query)
            data = []
            
            
            # Create a workbook and add a worksheet.
            self.path = app.config['UPLOAD_FOLDER']+"reports/"
            
            id = ObjectId()
            name = 'Users-'+str(id)+'.xlsx'
            filename = self.path+name   
            
            
            
            self.users = {}
            
            self.ipm = []
            self.city_manager = []
            self.supervisor = defaultdict(lambda: defaultdict(list))
            self.fwp = defaultdict(lambda: defaultdict(list))
            
            for row in result:
                del row['profile_pic']
                row = getRow(row)
                
                if row['role'] == 4:
                    self.ipm.append(row)
                elif row['role'] == 3:
                    self.city_manager.append(row)
                elif row['role'] == 2:
                    self.supervisor[row['parent_id']][row['id']].append(row) 
                elif row['role'] == 1:
                    self.fwp[row['parent_id']][row['id']].append(row)
                
              
            #print(self.fwp)
            workbook = xlsxwriter.Workbook(filename)
            worksheet = workbook.add_worksheet("IPM")
            
            c = 0
            c = self.__insertWorksheet(c,'IPM',workbook,worksheet,self.ipm)
            c = self.__insertCityManager(c,'CITY MANAGER',workbook,worksheet,self.city_manager)
            
            
            worksheet.set_column(0, 8, 25)
            workbook.close()


            """df1 = pd.DataFrame(temp) 
            print(df1)
            writer = pd.ExcelWriter(filename, engine='xlsxwriter')
            df1.to_excel(writer, sheet_name="Users",index=False)
                
            writer.save()"""
            return {'status':'Ok','filename':name},200
            
        
        except Exception as e:
            return {'error':{"message":"Error " + str(e)}},400    

    
    
    def __insertCityManager(self,c,title,workbook,worksheet,data):
        for row in data:
            c = 0
            worksheet = workbook.add_worksheet(row['name'])
            worksheet.set_column(0, 8, 25)
            c = self.__insertWorksheet(c,title,workbook,worksheet,[row])
        
        
    def __insertWorksheet(self,c,title,workbook,worksheet,data):
        
        tittle_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        header_format = workbook.add_format({'align':'center','bold': True, 'font_color': '#9c0d09','bg_color':'#cacaca'})
        
        self.left_format = workbook.add_format({'align':'center','valign':'vcenter','bold': True, 'font_color': '#ffffff','bg_color':'#3c4146','border':1,'border_color':'#3c4146'})
        self.left_format.set_text_wrap()
        
        format1 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        format2 = workbook.add_format({'bold': False, 'font_color': '#3c4146','bg_color':'#ffffff','border':1,'border_color':'#3c4146'})
        
        
        worksheet.merge_range('B'+str(c+1)+':F'+str(c+1),title,tittle_format)   
        
        c += 1    
       
        worksheet.write(c,0,'',self.left_format)
        worksheet.write(c,1,'NAME',header_format)
        worksheet.write(c,2,'CODE',header_format)
        worksheet.write(c,3,'MOBILE',header_format)
        worksheet.write(c,4,'EMAIL',header_format)
        worksheet.write(c,5,'RATING',header_format)
        worksheet.write(c,6,'STATUS',header_format)
        worksheet.write(c,7,'ISLOCKED',header_format)
        worksheet.write(c,8,'CITY',header_format)
        
        for data1 in data:
            c += 1
            self.__insertRow(worksheet,c,data1,format1,format2)
            firstC = c
            #self.supervisor_name = ''
            if data1['role'] == 3:
                c += 2
                temp = self.supervisor[data1['id']]
                for k in temp:
                    r = temp[k]
                    self.supervisor_name = "SUPERVISOR : "+r[0]['name'] + " \n CODE : "+r[0]['code']
                    c = self.__insertWorksheet(c,"SUPERVISOR",workbook,worksheet,r) 
                    
            elif data1['role'] == 2:
                c += 1
                temp = self.fwp[data1['id']]
                fwp = []
                for k in temp:
                    r = temp[k]
                    fwp.append(r[0])
               
                c = self.__insertWorksheet(c,"FWP",workbook,worksheet,fwp)
                worksheet.merge_range('A'+str(firstC)+':A'+str(c-1),self.supervisor_name,self.left_format)
        return c+2
        
            
    def __insertRow(self,worksheet,c,row,format1,format2):   
        if (c % 2) == 0:  
            worksheet.set_row(c, cell_format=format1)
        else:
            worksheet.set_row(c, cell_format=format2) 
        
        worksheet.write(c,0,self.roles[row['role']],self.left_format)
        worksheet.write(c,1,row['name'])
        worksheet.write(c,2,row['code'])
        worksheet.write(c,3,row['mobile'])
        worksheet.write(c,4,row['email'])
        worksheet.write(c,5,row['rating'])
        worksheet.write(c,6,row['status'])
        worksheet.write(c,7,row['isLocked'])
        
        if str(row['city_id']) in self.cities:
            worksheet.write(c,8,self.cities[str(row['city_id'])])
        else:
            worksheet.write(c,8,'')
        
        
        
        
        
        
        
    
