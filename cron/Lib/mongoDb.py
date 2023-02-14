#!/usr/local/bin/python3

from pymongo import MongoClient
import time
from bson import ObjectId

class MongoDb:
   
    CLINET  = ""
    
    def __init__(self):
        self.connect()
    
    def connect(self):
        con = 1
        while con:
            try:
                self.CLINET = MongoClient('mongodb://pmi:Title321@127.0.0.1:27017/pmi')
                
                con = 0
            except Exception as e:
               
                time.sleep(5)
                con = 1  
    
    def get_client(self):
        return self.CLINET
    
    def getDb(self):
        return self.CLINET.pmi
    
    
    
            
    
    

  



