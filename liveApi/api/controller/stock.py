from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,getRow,check_permissions
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime
from bson import ObjectId

    
@apiV1.resource('/stock/today/<user_id>')
class Stock(Resource):
    decorators = [check_permissions]
    
    def __init__(self):
        self.create_fields = {'id': {'type': 'string','empty': False},
                              'credit': {'type': 'integer','empty': False,'required':True}
                              }
        
        self.debit_fields = {'id': {'type': 'string','empty': False},
                              'debit': {'type': 'integer','empty': False,'required':True}
                              }
        self.id = ObjectId()
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        self.setProducts()
        self.setDefaultStocks()
        
    def get(self,user_id):
        try:
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
           
            
            users = mongo.db.users.find({"parent_id":getId(user_id)})
            users = getData(users)
            user_ids = []
            users_dict = {}
                    
            for user in users:
                user_ids.append(getId(user['id']))
                del user['password']
                t = {}
                t['id'] = str(ObjectId())
                t['date'] = str(self.dateInput)
                t['user'] = user
                t['stock'] = self.defaultStocks
                t['step1_verify'] = 0
                t['step2_verify'] = 0
                t['step3_verify'] = 0
                t['step1_comments'] = ''
                t['step2_comments'] = ''
                t['step3_comments'] = ''
                t['list'] = []
                users_dict[user['id']] = t
            #print(user_ids)
            
            
            result = mongo.db.stocks.find({"user_id": {"$in": user_ids},"date":self.dateInput})
            
            if result:   
                for row in result:
                    t = users_dict[str(row['user_id'])]
                    t['id'] = str(row['_id'])
                    t['date'] = str(row['date'])
                    t['stock'] = self.getStocks(row['stock'])
                    t['step1_verify'] = row['step1_verify']
                    t['step2_verify'] = row['step2_verify']
                    t['step3_verify'] = row['step3_verify']
                    
                    list = []
                    for l in row['list']:
                        list.append(str(l))
                    t['list'] = list
                    
                    
                    """if row['step1_verify'] == 1:
                        t['step1_comments'] = row['step1_data']['comments']
                    if row['step2_verify'] == 1:
                        t['step2_comments'] = row['step2_data']['comments']
                    if row['step2_verify'] == 1:
                        t['step3_comments'] = row['step3_data']['comments']"""
                 
                    #users_dict[str(row['user_id'])] = t
            
            temp = []      
            for t in users_dict:
                temp.append(users_dict[t])
                
            return temp,200       
            #else:
            #    return {'error':{"message":"User stock is not found"}},404
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong " +str(e)}},400  
        
          
    """def get1(self,user_id):
        try:
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            result = mongo.db.users.find_one({'_id':getId(user_id)})
            #print(result)
            aggr = [{"$lookup": { "from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"}]
            
            if not result:
                return {'error':{"message":"User Id is not valid."}},400
            elif result['role'] == 1:
                aggr.append({"$match":{"user_id":getId(user_id),"date":self.dateInput}})
            else:
                aggr.append({"$match":{"user.parent_id":getId(user_id),"date":self.dateInput}})
            
            result = mongo.db.stocks.aggregate(aggr)
            temp = []                                   
            if result:   
                for row in result:
                    t = {}
                    t['id'] = row['_id']
                    t['date'] = row['date']
                    t['user'] = getRow(row['user'])
                    t['stock'] = self.getStocks(row['stock'])
                    
                    t['step1_verify'] = row['step1_verify']
                    t['step2_verify'] = row['step2_verify']
                    t['step3_verify'] = row['step3_verify']
                    t['list'] = ["5d83e1b06d559ad227214156","5d83e1b06d559ad227214156"]
                    
                    temp.append(getRow(t))
                    
                return temp,200       
            else:
                return {'error':{"message":"User stock is not found"}},404
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400"""
    
    
    def getStocks(self,stocks):
        try:
            temp = []
            if len(stocks) > 0:
                for key in stocks.keys():
                    temp.append({'id':key,'name':self.products[key],'stock':stocks[key]})
                return temp
            else:
                return self.defaultStocks
        except:
            return self.defaultStocks
        
    
    def setDefaultStocks(self):
        temp = []
        for key in self.products.keys():
            temp.append({'id':key,'name':self.products[key],'stock':{'credit':0,'debit':0}})
        
        self.defaultStocks = temp
        
    def setProducts(self):
        result = mongo.db.offer_products.find()
        products = {}
        for row in result:
            products[str(row['_id'])] = row['name']
         
        self.products = products
           
        """result = mongo.db.products.find_one({'_id':getId('5d981ae25581b73e99d6b5c7')})
        temp = []
        products = {}
        for row in result['variant']:
            products[str(row['id'])] = row['name']
        
        self.products = products"""
        
    def post(self,user_id):
        try:
            result = mongo.db.users.find_one({'_id':getId(user_id)})
            if not result:
                return {'error':{"message":"User Id is not valid."}},400
            elif result['role'] != 1:
                return {'error':{"message":"This user is not authorized to credit stock. "}},400
                
            result = mongo.db.offer_products.find({'status':1},{'_id':1})
            #for row in result:
            #    self.create_fields['id'] = {'type': 'integer','empty': False,'required':True,'allowed': [0, 1]}
            
            
            json = request.get_json()
            data = {}
            
            for row in json:
                #print(row)
                v = Validator(self.create_fields,allow_unknown=False)
                if not v.validate(row):
                    return {'error':v.errors},400
                
                data[row['id']] = {'credit':row['credit'],'debit':0}
               
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            myquery = {"user_id":getId(user_id),"date":self.dateInput}
            
            r = mongo.db.stocks.find_one(myquery)
            
            if r:
               
                for key in r['stock']:
                   value = r['stock'][key]
                   data[key]['debit'] = value['debit']
                  
                #print(data)   
                   
                newvalues = {"$set": {"stock" : data}}
            else:
                newvalues = {"$set": {"stock" : data,"list":[],"step1_verify":0,"step2_verify":0,"step3_verify":0,"step1_data":None,"step2_data":None,"step3_data":None}}
                
            r = mongo.db.stocks.update_one(myquery, newvalues,upsert=True)
            
            if r:
                return {'status':'ok'},201
            else:
                return {'error':{"message":"Something Wrong"}},400
            
            
            
        except Exception as e:
            #print(e)
            return {'error':{"message":"Something Wrong"}},400
        
    def put(self,user_id):
        json = request.get_json()
        
        v = Validator(self.debit_fields,allow_unknown=False)
        if not v.validate(json):
            return {'error':v.errors},400
        
        product_id = json['id'];
        debit = json['debit'];
        
        
        self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
        myquery = {"user_id":getId(user_id),"date":self.dateInput}
        newvalues = { "$inc": {"stock."+product_id+".debit": int(debit)} }
        
        r = mongo.db.stocks.update_one(myquery, newvalues)
        if r:
            return {'status':'ok'},200
        else:
            return {'error':{"message":"Something Wrong"}},400
             
"""

db.getCollection('today_outlet').update(
   { _id: ObjectId("5d989f835581b73e99d6cdbe") },
   { $inc: {"stock.5d981a525581b73e99d6b584.debit": NumberInt(1)} }
)

"""   

         
