from api import app, mongo, apiV1
from flask import request
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,requestJsonData
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
import pandas as pd
import numpy as np
import random 
from datetime import date,datetime,timedelta



@apiV1.resource('/web/graph')
class WebGraph(Resource):
    
    def __init__(self):
        self.update_fields = {'status': {'allowed': [0, 1]}}
        
    def post(self):
        try:
            json = request.get_json()
            #print(json)
            productResults = mongo.db.products.find()
            products = {}
            for row in productResults:
                products[str(row['_id'])] = row['name']
                
            
            productResults = mongo.db.offer_products.find()
            offerProducts = {}
            offerProductColors = {}
            for row in productResults:
                offerProducts[str(row['_id'])] = row['name']
                offerProductColors[str(row['_id'])] = row['color']
            
            
            query = {}   
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            fromDate = json['fromDate']+" 00:00:00"
            toDate = json['toDate']+ " 23:59:59"
            
            fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d %H:%M:%S")
            toDate1 = datetime.strptime(str(toDate),"%Y-%m-%d %H:%M:%S") # + timedelta(days=1)
            
            query['date'] = {"$gte": fromDate1, "$lt": toDate1}
            
            aggr = [{"$lookup": { "from": "outlet_activity", "localField": "activity_id", "foreignField": "_id", "as": "activity"}},{ "$unwind": "$activity"}]
            
                
            if json['city_id'] != 'all':
                query['city_id'] = getId(json['city_id'])
            
            #for City Manager Login
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                query['city_id'] = getId(self.user['city_id'])   
            
            if json['outlet_id'] != 'all':
                query['outlet_id'] = getId(json['outlet_id'])
                
            if json['area'] != 'all':
                query['area'] = json['area']
                
            if json['program'] != 'all':
                query['program'] = json['program']
                
            if json['brand_id'] != 'all':
                query['brands'] = getId(json['brand_id'])
            
            if json['offer_brand_id'] != 'all':
                query['offer_brand'] = getId(json['offer_brand_id'])
                
            if json['supervisor_id'] != 'all':
                user_ids = self.getUserBySupervisor(json['supervisor_id'])
                query['user_id'] = {"$in":user_ids}
                
            if json['fwp_id'] != 'all':
                query['user_id'] = getId(json['fwp_id'])
                
            if json['activity'] != 'all':
                query['activity.activity'] = json['activity']
                
            aggr.append({"$match":query})    
            aggr.append({ "$project": {'brands':1,'offer_brand':1,'user_id':1,'gender':1,'age':1,'area':1}})
            #result = mongo.db.miform.find(query,{'brands':1,'offer_brand':1,'user_id':1,'gender':1,'age':1,'area':1})
            
            #print(aggr)
            
            result = mongo.db.miform.aggregate(aggr)
            
            lists = list(result)
            total = len(lists)
            
            achievement = {'cc':total,'ecc':total,'total':total+total}
            
            df = pd.DataFrame(lists)
            #print(df) 
            
            # Brand table function
            brand_label = []
            brand_value = []
            brand_total = 0
            try:
                grouped = df.groupby('brands')
                brandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                
                brandTable = brandTable.to_dict('index')
                
                for key in brandTable.keys():
                    value = brandTable[key]['_id']
                    brand_label.append(products[str(key)])
                    brand_value.append(value)
                    brand_total = brand_total + value
            except:
                pass
                
            
            # Offered Brand table function
            offerBrand_label = []
            offerBrand_value = []
            offerBrand_color = []
            offerBrand_total = 0
            try:
                grouped = df.groupby('offer_brand')
                offerBrandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                
                offerBrandTable = offerBrandTable.to_dict('index')
                
                for key in offerBrandTable.keys():
                    value = offerBrandTable[key]['_id']
                    offerBrand_label.append(offerProducts[str(key)])
                    offerBrand_value.append(value)
                    offerBrand_color.append(offerProductColors[str(key)])
                    offerBrand_total = offerBrand_total + value
            except:
                pass
                 
                    
            # Area table function   
            area_label = []
            area_value = []
            area_total = 0 
            try: 
                grouped = df.groupby('area')
                areaTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                
                areaTable = areaTable.to_dict('index')
                
                for key in areaTable.keys():
                    value = areaTable[key]['_id']
                    #area_label.append(str(key) + " : "+str(value))
                    area_label.append(key)
                    area_value.append(value)
                    area_total = area_total + value
            except:
                pass    
            
            
                
                
            # Gender table function
            gender = {'MALE':0,'FEMALE':0,'total':0}
            try:
                grouped = df.groupby('gender')
                genderTable = grouped.agg(np.size).sort_values(by='_id', ascending=False)
                
                
                
                genderTable = genderTable.to_dict('index')
                if 'MALE' in genderTable:
                    gender['MALE'] = genderTable['MALE']['_id']
                if 'FEMALE' in genderTable:
                    gender['FEMALE'] = genderTable['FEMALE']['_id']
                    
                gender['total'] = gender['MALE'] + gender['FEMALE']
            except:
                pass
            
            # Age table function
            age = {'18-24':0,'25-29':0,'30-34':0,'35-44':0,'>44':0,'total':0}
            try:
                grouped = df.groupby('age')
                ageTable = grouped.agg(np.size)
                    
                ageTable = ageTable.to_dict('index')
                ageTotal = 0
                
                for key in ageTable.keys():
                    value = ageTable[key]['_id']
                    key = int(key)
                    ageTotal = ageTotal+value
                    
                    if key in range(18,25):
                        age['18-24'] = age['18-24']+value
                    elif key in range(25,30):
                        age['25-29'] = age['25-29']+value
                    elif key in range(30,35):
                        age['30-34'] = age['30-34']+value
                    elif key in range(35,45):
                        age['35-44'] = age['35-44']+value
                    else:
                        age['>44'] = age['>44']+value
                
                age['total'] = ageTotal
            
            except:
                pass
            
                
            data = {'ageSplit':age,
                    'gender':gender,
                    'achievement':achievement,
                    'brand':{'label':brand_label,'value':brand_value,'total':brand_total},
                    'offerBrand':{'label':offerBrand_label,'value':offerBrand_value,'color':offerBrand_color,'total':offerBrand_total},
                    'area':{'label':area_label,'value':area_value,'total':area_total}}
            
            return data,200
            
            
        except Exception as e:
            print(e)
            data = {'ageSplit':{'18-24':0,'25-29':0,'30-34':0,'35-44':0,'>44':0,'total':0},
                    'gender':{'MALE':0,'FEMALE':0,'total':0},
                    'achievement':{'cc':0,'ecc':0,'total':0},
                    'brand':{'label':[],'value':[],'total':0},
                    'offerBrand':{'label':[],'value':[],'color':[],'total':0},
                    'area':{'label':[],'value':[],'total':0}}
            return data,200
    
    
    #add area in miform
    def get1(self):
        result = mongo.db.miform.find()
        forms = []
        for row in result:
            forms.append(row)
        
        for row in forms:
            #row1 = mongo.db.outlet.find_one({"_id":row['outlet_id']})
            #mongo.db.miform.update_one({"_id":row['_id']},{"$set":{'area':row1['area'].upper(), 'program':row1['type'] }})
            
            p = [ 
            "5e12bb9c5581b73e99fbb167", 
            "5e12bbca5581b73e99fbb18b", 
            "5e12bc775581b73e99fbb273", 
            "5e12bc815581b73e99fbb293", 
            "5e12bcb95581b73e99fbb2bb", 
            "5e12bcda5581b73e99fbb2d4", 
            "5e12bce85581b73e99fbb2e0", 
            "5e12bcf95581b73e99fbb2ee", 
            "5e12bd075581b73e99fbb30a", 
            "5e12bd1d5581b73e99fbb31a", 
            "5e12bd285581b73e99fbb325"
        ]
            r1 = random.randint(0, 10) 
            print(p[r1])
            #mongo.db.miform.update_one({"_id":row['_id']},{"$set":{'offer_brand':getId(p[r1])}})
            
    def getUserBySupervisor(self,supervisor_id):
        result = mongo.db.users.find({"parent_id": getId(supervisor_id)})
        
        user_ids = []
        for row in result:
            user_ids.append(row['_id'])
        return user_ids
            
        #data[str(row['parent_id'])]['supervisor'].append({'id':str(c,'name':row['name']})     
 
@apiV1.resource('/web/graph/summary')
class WebGraphSummary(Resource):   
    
    def post(self):
        try:
            json = request.get_json()
            outlet_query = {}   
            user_query = {}   
            fwp_query = {}
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            fromDate = json['fromDate']+" 00:00:00"
            toDate = json['toDate']+ " 23:59:59"
            
            
            fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d %H:%M:%S")
            toDate1 = datetime.strptime(str(toDate),"%Y-%m-%d %H:%M:%S") # + timedelta(days=1)
            
            if str(json['fromDate']) == str(json['toDate']):
                outlet_query['date'] = fromDate1
                user_query['date'] = fromDate1
            else:
                outlet_query['date'] = {"$gte": fromDate1, "$lt": toDate1}
                user_query['date'] = {"$gte": fromDate1, "$lt": toDate1}
                
            if json['city_id'] != 'all':
                outlet_query['outlet.city_id'] = getId(json['city_id'])
                user_query['user.city_id'] = getId(json['city_id'])
                fwp_query['city_id'] = getId(json['city_id'])
            
            #for City Manager Login
            self.user = getCurrentUser() 
            if self.user['role'] == 3:
                outlet_query['outlet.city_id'] = getId(self.user['city_id'])
                user_query['user.city_id'] = getId(self.user['city_id'])
            
            if json['outlet_id'] != 'all':
                outlet_query['outlet_id'] = getId(json['outlet_id'])
                
            if json['area'] != 'all':
                outlet_query['outlet.area'] = json['area']
                
            if json['program'] != 'all':
                outlet_query['outlet.type'] = json['program']
                
            if json['supervisor_id'] != 'all':
                user_ids = self.getUserBySupervisor(json['supervisor_id'])
                outlet_query['supervisor_id'] = getId(json['supervisor_id'])
                user_query['user_id'] = {"$in":user_ids}
                
            if json['fwp_id'] != 'all':
                outlet_query['fwp_id'] = getId(json['fwp_id'])
                user_query['user_id'] = getId(json['fwp_id'])
                
            if json['activity'] != 'all':
                outlet_query['activity'] = json['activity']
            
            
            data = {'total_working_days':0,'total_man_days':0,'total_outlet':0,'unique_outlet':0,'total_fwp':0}
            
            user_query['user.role'] = 1
            
            aggr = [{"$lookup": { "from": "users", "localField": "user_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"}]
            aggr.append({"$match":user_query})
           
            #print(aggr)
            result = mongo.db.attendance.aggregate(aggr)
            #result = mongo.db.attendance.find({"date":{"$gte": fromDate1, "$lt": toDate1}})
            df = pd.DataFrame(list(result))
            
            #print(df)
            
            try:
                grouped = df.groupby('date')
                dateTable = grouped.agg(np.size)
                dateTable = dateTable.to_dict('index')
                
                #print(dateTable)
                for key in dateTable:
                    value = dateTable[key]['_id']
    
                    data['total_working_days'] = data['total_working_days'] + 1
                    data['total_man_days'] = data['total_man_days'] + value
            except:
                pass
            
            #query = {}
            #print(data)
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            aggr.append({"$match":outlet_query})
            
            #print(aggr)
            
            #result = mongo.db.outlet_activity.find(query,{'_id':1,'outlet_id':1})
            
            #print(aggr)
            
            result = mongo.db.outlet_activity.aggregate(aggr)
            temp = []
            
            #totla cc for achievement
            total_cc = 0
            for row in result:
                if len(row['checkin_activity']) > 0:
                    temp.append(row)
                if 'cc' in row:
                    total_cc = total_cc + row['cc']
                    
            df = pd.DataFrame(temp)
            #print(df)
            
            try:
                grouped = df.groupby('outlet_id')
                outletTable = grouped.agg(np.size)
                outletTable = outletTable.to_dict('index')
                
                for key in outletTable:
                    value = outletTable[key]['_id']
                    data['total_outlet'] = data['total_outlet'] + value
                    data['unique_outlet'] = data['unique_outlet'] + 1
            except:
                pass
            
            
            fwp_query['role'] = 1
            fwp_query['status'] = 1
            result = mongo.db.users.find(fwp_query)
            data['total_fwp'] = result.count()
            
            data['total_cc'] = total_cc
            
            
            return data,200
        except Exception as e:
            #print("Error Summary: "+str(e))
            return {'total_outlet':0,'unique_outlet':0,'total_working_days':0,'total_man_days':0,'total_fwp':0,'total_cc':0}        
        
    
    def getUserBySupervisor(self,supervisor_id):
        result = mongo.db.users.find({"parent_id": getId(supervisor_id)})
        
        user_ids = []
        for row in result:
            user_ids.append(row['_id'])
        return user_ids
        
          
@apiV1.resource('/outlet/select/<city>/<area>')
class OutletSelectByCity(Resource): 
    def get(self,city,area):
        try:
           
            query = {}
            if area != 'all':
                query['area'] = area
                
            query['city_id'] = getId(city)
            #print(query)
            users = mongo.db.outlet.find(query).sort([('name',-1)])
           
            data = []
            
            for row in users:
                data.append({'id':str(row['_id']),'name':row['code']})
                
            return data,200
        except Exception as e:
            print(e)
            return [],200        
        
