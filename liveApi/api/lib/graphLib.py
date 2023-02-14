from api import app, mongo
from api.lib.helper import getId,getCurrentUser,getCurrentUserId
from datetime import date,datetime,timedelta
import pandas as pd
import numpy as np
import calendar
import pendulum




class graphLib:
    
    def __init__(self):
      
        d = date.today() #+ timedelta(days=-1)
        startDate = str(d)+ " 00:00:00"
        startDate  =  datetime.strptime(str(startDate),"%Y-%m-%d %H:%M:%S")
        
        endDate = str(d)+ " 23:59:59"
        endDate  =  datetime.strptime(str(endDate),"%Y-%m-%d %H:%M:%S")
        
        self.startDate = startDate
        self.endDate = endDate
        
        self.months = self.getLast6MonthRange()
        self.weeks = self.getLast6WeekRange()
        
    
    def getChildUserIds(self,parent_id,isFWP = False):
        try:
            data = []
            if isFWP:
                result = mongo.db.users.find({'_id':parent_id},{'_id':1})
            else:
                result = mongo.db.users.find({'parent_id':parent_id},{'_id':1})
            
            for row in result:
                data.append(row['_id'])
                
            return data
        except:
            return []
        
    def getChildUsers(self,parent_id,isFWP = False):
        try:
            data = {}
            if isFWP:
                result = mongo.db.users.find({'_id':parent_id},{'name':1})
            else:
                result = mongo.db.users.find({'parent_id':parent_id},{'name':1})
            
            for row in result:
                data[str(row['_id'])] = {'label':row['name'],'value':0}
                
            return data
        except:
            return {}
        
    def getOfferBrands(self):
        try:
            productResults = mongo.db.offer_products.find()
            offerProducts = {}
            for row in productResults:
                offerProducts[str(row['_id'])] = {'label':row['name'],'value':0}
            return offerProducts
        except:
            return {}
    
    
    
    
    
    
    
    def getMonthWorkingDays(self,isFWP = False):
        row = self.months[0]
        return self.getWorkingDays(row['startDate'],row['endDate'],isFWP)
    
    def getWeekWorkingDays(self,isFWP = False):
        row = self.weeks[0]
        return self.getWorkingDays(row['startDate'],row['endDate'],isFWP)
    
    def getTodayWorkingDays(self,isFWP = False):
        #row = self.months[1]
        return self.getWorkingDays(self.startDate,self.endDate,isFWP)
    
    def getWorkingDays(self,startDate,endDate,isFWP = False):
        
        try:           
            user_ids = self.getChildUserIds(getId(getCurrentUserId()),isFWP)
            userList = self.getChildUsers(getId(getCurrentUserId()),isFWP)
            
            count = 0
            
            query = {}
            query['date'] = {'$gte': startDate, '$lt': endDate}
            query['user_id']  = {"$in":user_ids}
            
            
          
            result = mongo.db.attendance.find(query,{'user_id':1})
            #print(list(result))
            df = pd.DataFrame(list(result))
            #print(df)
            
            # Offered Brand table function
            userTable_label = []
            userTable_value = []
            try:
                grouped = df.groupby('user_id')
                userTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                
                userTable = userTable.to_dict('index')
               
                for key in userTable.keys():
                    value = userTable[key]['_id']
                    userList[str(key)]['value'] = value
                    count = count+value
            except Exception as e:
                print("Grouping Error: "+str(e))
            
            for row in userList.values():
                userTable_label.append(row['label'])
                userTable_value.append(row['value'])
            
            #print({'total':count,'label':userTable_label,'value':userTable_value})    
            return {'total':count,'label':userTable_label,'value':userTable_value}
        
        except Exception as e:
            #print(e)
            return {'total':0,'label':[],'value':[]}
    
    
    
    def getMonthWorkingHours(self,isFWP = False):
        row = self.months[0]
        return self.getWorkingHours(row['startDate'],row['endDate'],isFWP)
    
    def getWeekWorkingHours(self,isFWP = False):
        row = self.weeks[0]
        return self.getWorkingHours(row['startDate'],row['endDate'],isFWP)
    
    def getTodayWorkingHours(self,isFWP = False):
        #row = self.months[1]
        return self.getWorkingHours(self.startDate,self.endDate,isFWP)
    
    def getWorkingHours(self,startDate,endDate,isFWP = False):
        
        try:           
            user_ids = self.getChildUserIds(getId(getCurrentUserId()),isFWP)
            userList = self.getChildUsers(getId(getCurrentUserId()),isFWP)
            
            count = 0
            
            query = {}
            query['date'] = {'$gte': startDate, '$lt': endDate}
            query['fwp_id']  = {"$in":user_ids}
            
            #print(query)
            
          
            result = mongo.db.outlet_activity.find(query,{'fwp_id':1,'start_time':1,'end_time':1,'checkin_activity':1})
            #print(list(result))
            lists = []
            fwp = {}
            for row in result:
                #print(row['checkin_activity'])
                duration = row['end_time'] - row['start_time']
                duration = int(duration)
                count = duration + count
                """for checkin in row['checkin_activity']:
                    start = checkin['start']['date']
                    end = checkin['end']['date']
                    if end == None:
                        duration = 0 
                    else:
                        duration = end - start
                    print("Start : "+ str(start)+"  - End : "+str(end)+"\n")
                print("Duration : "+ str(duration)+"\n")"""
                userList[str(row['fwp_id'])]['value'] = duration
            
            #print(userList)
            
            # Offered Brand table function
            userTable_label = []
            userTable_value = []
            
            
            for row in userList.values():
                userTable_label.append(row['label'])
                userTable_value.append(row['value'])
            
            #print({'total':count,'label':userTable_label,'value':userTable_value})    
            return {'total':count,'label':userTable_label,'value':userTable_value}
        
        except Exception as e:
            print(e)
            return {'total':0,'label':[],'value':[]}
    
    
    
    
    
    def getMonthProductivityReport(self):
        row = self.months[0]
        return self.getProductivityReport(row['startDate'],row['endDate'])
        
    def getWeekProductivityReport(self):
        row = self.weeks[0]
        return self.getProductivityReport(row['startDate'],row['endDate'])    
    
    def getTodayProductivityReport(self):
        #row = self.weeks[0]
        #print(self.startDate)
        #print(self.endDate)
        return self.getProductivityReport(self.startDate,self.endDate)    
    
    def getProductivityReport(self,startDate,endDate):
        
        try:
        
            user_ids = self.getChildUserIds(getId(getCurrentUserId()))
            offerProducts = self.getOfferBrands()
            count = 0
           
           
            query = {}
            query['date'] = {'$gte': startDate, '$lt': endDate}
            query['user_id']  = {"$in":user_ids}
            
          
            result = mongo.db.miform.find(query,{'offer_brand':1})
            df = pd.DataFrame(list(result))
            
            # Offered Brand table function
            offerBrand_label = []
            offerBrand_value = []
            try:
                grouped = df.groupby('offer_brand')
                offerBrandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
                
                offerBrandTable = offerBrandTable.to_dict('index')
               
                for key in offerBrandTable.keys():
                    value = offerBrandTable[key]['_id']
                    offerProducts[str(key)]['value'] = value
                    count = count+value
            except Exception as e:
                print("Grouping Error: "+str(e))
            
            for row in offerProducts.values():
                #print(row)
                offerBrand_label.append(row['label'])
                offerBrand_value.append(row['value'])
                
            return {'total':count,'label':offerBrand_label,'value':offerBrand_value}
        
        except Exception as e:
            print(e)
            return {'total':0,'label':[],'value':[]}
        
    def getMonthECC(self):
        query = {}
        query['user_id'] = getId(getCurrentUserId())
        
        label = []
        value = []
        count = 0
        for row in self.months:
            query['date'] = {'$gte': row['startDate'], '$lt': row['endDate']}
            result = mongo.db.miform.find(query)
                
            total = result.count()
            count = count + total
            value.append(total)
            label.append(row['startDate'].strftime("%b"))
            
        return {'total':count,'label':label,'value':value}
    
    
    def getWeekECC(self):
        query = {}
        query['user_id'] = getId(getCurrentUserId())
        
        label = []
        value = []
        count = 0
        i = 0
        for row in self.weeks:
            query['date'] = {'$gte': row['startDate'], '$lt': row['endDate']}
            result = mongo.db.miform.find(query)
                
            total = result.count()
            count = count + total
            i = i+1
            value.append(total)
            label.append(row['startDate'].strftime("%d"))
            
        return {'total':count,'label':label,'value':value}
       
    
    
    
    
    
    
    
    # CityManager Age Split
    def getMonthIPMStatics(self):
        row = self.months[0]
        return self.getIPMStatics(row['startDate'],row['endDate'])
        
    def getWeekIPMStatics(self):
        row = self.weeks[0]
        return self.getIPMStatics(row['startDate'],row['endDate'])    
    
    def getTodayIPMStatics(self):
        return self.getIPMStatics(self.startDate,self.endDate)    
    
    def getIPMStatics(self,startDate,endDate):
        
        try:
        
            productResults = mongo.db.products.find()
            products = {}
            for row in productResults:
                products[str(row['_id'])] = row['name']
                
            
            productResults = mongo.db.offer_products.find()
            offerProducts = {}
            for row in productResults:
                offerProducts[str(row['_id'])] = row['name']
                
            user_ids = self.getChildUserIds(getId(getCurrentUserId()))
            #offerProducts = self.getOfferBrands()
            count = 0
           
           
            query = {}
            query['date'] = {'$gte': startDate, '$lt': endDate}
            #query['fwp_id']  = {"$in":user_ids}
            
          
            result = mongo.db.miform.find(query,{'brands':1,'offer_brand':1,'user_id':1,'age':1})
            
            total = result.count()
           
            df = pd.DataFrame(list(result))
            #print(df) 
            
            # Brand table function
            grouped = df.groupby('brands')
            brandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
            
            brandTable = brandTable.to_dict('index')
            brand_label = []
            brand_value = []
            brand_total = 0
            for key in brandTable.keys():
                value = brandTable[key]['_id']
                brand_label.append(products[str(key)])
                brand_value.append(value)
                brand_total = brand_total + value
                
            
            # Offered Brand table function
            grouped = df.groupby('offer_brand')
            offerBrandTable = grouped.agg(np.size) #sort_values(by='_id', ascending=False)
            
            offerBrandTable = offerBrandTable.to_dict('index')
            offerBrand_label = []
            offerBrand_value = []
            offerBrand_total = 0
            for key in offerBrandTable.keys():
                value = offerBrandTable[key]['_id']
                offerBrand_label.append(offerProducts[str(key)])
                offerBrand_value.append(value)
                offerBrand_total = offerBrand_total + value
                
                    
            
            
            # Age table function
            grouped = df.groupby('age')
            ageTable = grouped.agg(np.size)
                
            ageTable = ageTable.to_dict('index')
            
            age = {'18-24':0,'25-29':0,'30-34':0,'35-44':0,'>44':0}
            age_total = 0
            
            for key in ageTable.keys():
                value = ageTable[key]['_id']
                key = int(key)
                
                if key in range(18,24):
                    age['18-24'] = age['18-24']+value
                elif key in range(25,29):
                    age['25-29'] = age['25-29']+value
                elif key in range(30,34):
                    age['30-34'] = age['30-34']+value
                elif key in range(35,44):
                    age['35-44'] = age['35-44']+value
                else:
                    age['>44'] = age['>44']+value
                
                age_total =  age_total + value
            
           
                
            data = {'age':{'total':age_total,'label':list(age.keys()),'value':list(age.values())},
                    'brand':{'total':brand_total,'label':brand_label,'value':brand_value},
                    'offerBrand':{'total':offerBrand_total,'label':offerBrand_label,'value':offerBrand_value}}
                    
            
            return data
        
        except Exception as e:
            print("Error : "+str(e))
            data = {'age':{'total':0,'label':[],'value':[]},
                    'brand':{'total':0,'label':[],'value':[]},
                    'offerBrand':{'total':0,'label':[],'value':[]}}
            return data
    
    
    
    
    
    
    
    
    
    
    def getLast6MonthRange(self):
        list = [d.replace(day=1) for d in [date.today()-timedelta(weeks=4*i) for i in range(0,1)]]   
        
        months = []
        
        #print(list)
        
        for row in list:
            date1  =  datetime.strptime(str(row),"%Y-%m-%d")
            startDate = date1
            endDate = date1.replace(day = calendar.monthrange(date1.year, date1.month)[1])
            
            months.append({'startDate':startDate,'endDate':endDate})
            
        return months
    
    
    
    def getLast6WeekRange_bk1(self):
        today = pendulum.today()
        list = []
        
        for i in range(0,6):
            list.append(today.subtract(weeks=i))
        
        
        months = []
        
        #print(list)
        
        for row in list:
            #temp = str(row).replace("T00:00:00+05:30", "")
            temp = str(row.add(days = -7)).replace("T00:00:00+05:30", "")
            date1  =  datetime.strptime(temp,"%Y-%m-%d")
            startDate = date1
            
            temp = str(row.add(days = -1)).replace("T00:00:00+05:30", "")
            endDate = datetime.strptime(temp,"%Y-%m-%d")
            
            months.append({'startDate':startDate,'endDate':endDate})
            
        return months    
    
    def getLast6WeekRange(self):
        today = pendulum.today()
        list = []
        
        for i in range(0,6):
            list.append(today.subtract(days=i))
        
        
        months = []
        
        for row in list:
            temp = str(row).replace("T00:00:00+05:30", " 00:00:00")
            date1  =  datetime.strptime(temp,"%Y-%m-%d %H:%M:%S")
            startDate = date1
            
            temp = str(row).replace("T00:00:00+05:30", " 23:59:59")
            endDate = datetime.strptime(temp,"%Y-%m-%d %H:%M:%S")
            
            months.append({'startDate':startDate,'endDate':endDate})
            
        return months    
            
            
