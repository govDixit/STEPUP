from api import app, mongo, apiV1
from flask import request, send_file
from flask_restful import Resource
from api.lib.helper import getData,getId,getCurrentUser,getActivity
from cerberus import Validator
from pymongo.errors import DuplicateKeyError 
import json
from datetime import date,datetime,timedelta
from bson import ObjectId
from api.lib.outletLib import OutletLib
import hashlib 
from bson.int64 import Int64



@apiV1.resource('/outlet/web/activity')
class OutletWebActivity(Resource):
    
    def get(self):
        try:
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search')
            city_id = request.args.get('city_id','0')
            fromDate = request.args.get('fromDate',self.dateInput)
            toDate = request.args.get('toDate',self.dateInput)
            
            fwp_code = request.args.get('fwp_code','')
            outlet_code = request.args.get('outlet_code','')
            
            
            date.today() + timedelta(days=10)
        
            fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d")
            toDate1 = datetime.strptime(str(toDate),"%Y-%m-%d") + timedelta(days=1)
            
            user = getCurrentUser() 
            
            query = {}
            
           
            if fromDate == toDate:
                query['date'] = fromDate1
            else:
                query['date'] = {"$gte": fromDate1, "$lt": toDate1}
            #print(query)
            
            
            
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            #aggr.append({"$lookup": { "from": "user", "localField": "fwp_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"})
               
            aggr.append({"$match":{"date":{"$gte": fromDate1, "$lt": toDate1}}})
            
            if city_id != '0':
                aggr.append({"$match":{"outlet.city_id":getId(city_id)}})
            
            
            if fwp_code != '':
                fwp_id  = self.getUserId(fwp_code)
                if fwp_id:
                    aggr.append({"$match":{"fwp_id":fwp_id}})
                    
            if outlet_code != '':
                aggr.append({"$match":{"outlet.code":outlet_code}})
                #aggr.append({"$match": {"$or": [{'outlet.name':{'$regex' : search, '$options' : 'i'}},{'outlet.code':search}] }}) 
           
            aggr.append({"$sort" : {'_id' : -1} })
            
            aggr.append({"$facet" : {"outlet_activity":[{"$skip":start},{"$limit":10}],"totalCount":[{"$count":"count"}] } })
            
        
            #print(aggr)
            
            result = mongo.db.outlet_activity.aggregate(aggr)
            total  = 0 #result.count()
            aResult = []
            for row in result:
                if len(row['totalCount']) > 0:
                    total = row['totalCount'][0]['count']
                aResult = row['outlet_activity']
               
           
            temp = []
            fwp_ids = []
            for o in aResult:
                #print(o)
                #o = activities[str(row['_id'])]
                fwp_ids.append(o['fwp_id'])
                row = {}
                row['name'] = o['outlet']['name']
                row['code'] = o['outlet']['code']
                row['date'] = str(o['date']).replace(" 00:00:00", "")
                row['activity_id'] = str(o['_id'])
                row['checkin'] = o['checkin']
                row['checkin_id'] = o['checkin_id']
                row['selfie'] = o['selfie']
                row['break'] = o['break']
                row['break_id'] = o['break_id']
                row['fwp_id'] = o['fwp_id']
                row['supervisor_id'] = o['supervisor_id']
                row['citymanager_id'] =  o['citymanager_id'] if 'citymanager_id' in o else 0
                row['start_time'] = o['start_time']
                row['end_time'] = o['end_time']
                row['meeting'] = str(o['meeting'])
                row['activity'] = o['activity']
                row['cycle'] = o['cycle']
                row['community'] = o['community']
                
                
                    
                row['checkin_activity'] = getActivity(o['checkin_activity'])
                
                row['status'] = o['status']
                #print(row['outlet']['checkin_activity'])
                temp.append(getData(row))
                
                
            # User name and code store
            fwp = {}
            result = mongo.db.users.find({"_id":{'$in':fwp_ids}})
            for row in result:
                fwp[str(row['_id'])] = {'name':row['name'],'code':row['code']}
           
            
            for r in temp:
                if r['fwp_id'] in fwp:
                    r['fwp'] = fwp[r['fwp_id']]
                else:
                    r['fwp'] = {'name':'--','code':'--'}
            
           
                    
            data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
            data['data'] = temp
            return data,200
           
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong "+str(e)}},400

        
    def getUserId(self,code):
        try:
            user = mongo.db.users.find_one({'code':code})
            if user:
                return user['_id']
            else:
                return False
            
        except:
            return False
        
    def get_bk1(self):
        try:
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            length = int(request.args.get('length',10))
            start = int(request.args.get('start',0))
            search = request.args.get('search')
            fromDate = request.args.get('fromDate',self.dateInput)
            toDate = request.args.get('toDate',self.dateInput)
        
            user = getCurrentUser() 
            aggr = [{"$lookup": { "from": "outlet", "localField": "outlet_id", "foreignField": "_id", "as": "outlet"}},{ "$unwind": "$outlet"}]
            
            aggr.append({"$lookup": { "from": "user", "localField": "fwp_id", "foreignField": "_id", "as": "user"}},{ "$unwind": "$user"})
           
            
            
            self.dateInput = datetime.strptime(str(date.today()),"%Y-%m-%d")
            
            if user['role'] == 1:
                aggr.append({"$match":{"fwp_id":getId(user['user_id']),"date":self.dateInput}})
            elif user['role'] == 2:
                aggr.append({"$match":{"supervisor_id":getId(user['user_id']),"date":self.dateInput}})
            elif user['role'] == 3:
                aggr.append({"$match":{"citymanager_id":getId(user['user_id']),"date":self.dateInput}})
            else:
                aggr.append({"$match":{"date":self.dateInput}})
            
            """aggr.append({"$limit" : length})
            aggr.append({"$skip" : start})
            aggr.append({"$group" : {"_id": None,"count": { "$sum": 1 } } })"""
            
            #print(aggr)
            result = mongo.db.outlet_activity.aggregate(aggr)
            total = 50 #result.count()
            
            temp = []
            if result:   
                for row in result:
                    #print(row)
                    row['outlet']['date'] = str(row['date']).replace(" 00:00:00", "")
                    row['outlet']['activity_id'] = str(row['_id'])
                    row['outlet']['checkin'] = row['checkin']
                    row['outlet']['checkin_id'] = row['checkin_id']
                    row['outlet']['selfie'] = row['selfie']
                    row['outlet']['break'] = row['break']
                    row['outlet']['break_id'] = row['break_id']
                    row['outlet']['fwp_id'] = row['fwp_id']
                    row['outlet']['supervisor_id'] = row['supervisor_id']
                    row['outlet']['citymanager_id'] = row['citymanager_id']
                   
                    row['outlet']['checkin_activity'] = getActivity(row['checkin_activity'])
                    #print(row['outlet']['checkin_activity'])
                    row['outlet']['fwp'] = {'name':row['user']['name'],'code':row['user']['code']}
                   
                   
                    temp.append(getData(row['outlet']))
                        
                data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
                data['data'] = temp
                return data,200
            else:
                return {'error':{"message":"Outlet is not found"}},404
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400

@apiV1.resource('/outlet/web/checkins/<id>')
class OutletWebCheckinsActivityById(Resource):
    
    def get(self,id):
        try:
            result = mongo.db.outlet_activity.find_one({'_id':getId(id)})            
            if result:  
                data = getActivity(result['checkin_activity'])
                return data,200
            else:
                return [],200
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400



@apiV1.resource('/outlet/web/break/<id>')
class OutletWebBreakActivityById(Resource):
    
    def get(self,id):
        try:
            result = mongo.db.outlet_activity.find_one({'_id':getId(id)})            
            if result:  
                data = getActivity(result['break_activity'])
                return data,200
            else:
                return [],200
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400



@apiV1.resource('/outlet/web/route/status')
class OutletWebChangeRoutePlanStatus(Resource):
    
    def post(self):
        try:
            json = request.get_json()
            
            myquery = {"_id":getId(json['id'])}
            newvalues = {"$set": {'status':json['status']}}
            mongo.db.outlet_activity.update_one(myquery, newvalues)
            mongo.db.today_outlet.update_one(myquery, newvalues)
            return {'status':'Ok'},200
        
        except Exception as e:
            #print(e)
            return {'error':{"message":"Something Wrong"}},400
        
        
@apiV1.resource('/checkin/download/<filename>')
class CheckinDownload(Resource):
    def get(self,filename):
        try:
            path = "../"+app.config['UPLOAD_FOLDER']+'checkin/'+filename
            return send_file(path, as_attachment=True)
        except:
            return {'error':{"message":"Something Wrong."}},400   


