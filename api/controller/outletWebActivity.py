from api import app, mongo, apiV1
from flask import request
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
            fromDate = request.args.get('fromDate',self.dateInput)
            toDate = request.args.get('toDate',self.dateInput)
            
            date.today() + timedelta(days=10)
        
            fromDate1 = datetime.strptime(str(fromDate),"%Y-%m-%d")
            toDate1 = datetime.strptime(str(toDate),"%Y-%m-%d") + timedelta(days=1)
            
            user = getCurrentUser() 
            
            query = {}
            
            if search != '':
                query['$or'] = [{'name':{'$regex' : search, '$options' : 'i'}}]
            
            if fromDate == toDate:
                query['date'] = fromDate1
            else:
                query['date'] = {"$gte": fromDate1, "$lt": toDate1}
            #print(query)
            result = mongo.db.outlet_activity.find(query).skip(start).limit(length).sort([('_id', -1)])
            total  = result.count()
            
            outlet_ids = []
            activities = {}
            for row in result:
                outlet_ids.append(row['outlet_id'])
                activities[str(row['outlet_id'])] = row;
            
            
            result = mongo.db.outlet.find({"_id": {"$in": outlet_ids}})
            
            
            temp = []
            if result:   
                for row in result:
                    o = activities[str(row['_id'])]
                    row['date'] = str(o['date']).replace(" 00:00:00", "")
                    row['activity_id'] = str(o['_id'])
                    row['checkin'] = o['checkin']
                    row['checkin_id'] = o['checkin_id']
                    row['selfie'] = o['selfie']
                    row['break'] = o['break']
                    row['break_id'] = o['break_id']
                    row['fwp_id'] = o['fwp_id']
                    row['supervisor_id'] = o['supervisor_id']
                    row['citymanager_id'] = o['citymanager_id']
                    row['start_time'] = o['start_time']
                    row['end_time'] = o['end_time']
                    row['meeting'] = o['meeting']
                    row['activity'] = o['activity']
                    row['cycle'] = o['cycle']
                    row['community'] = o['community']
                   
                    row['checkin_activity'] = getActivity(o['checkin_activity'])
                    #print(row['outlet']['checkin_activity'])
                    
                    temp.append(getData(row))
                        
                data = {"draw":total,"recordsTotal":total,"recordsFiltered":total,"data":[]}
                data['data'] = temp
                return data,200
            else:
                return {'error':{"message":"Outlet is not found"}},404
            
        except Exception as e:
            print(e)
            return {'error':{"message":"Something Wrong"}},400


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


