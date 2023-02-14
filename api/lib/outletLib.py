from api import app, mongo
from api.lib.helper import getId,getCurrentUser
from datetime import datetime
from werkzeug.utils import secure_filename
import uuid,os

class OutletLib:
    def __init__(self):
        self.create_fields = {'coardinates': {'type': 'dict','required': True,
                                              'schema': {'latitude': {'type': 'float'},'longitude': {'type': 'float'}}
                                              }}
        self.dateError = {'error':{"message":"Date format is not a valid."}},400  
        self.userIdError = {'error':{"message":"User Id is not a valid."}},400 
         
        self.hr = {}
        #{'fwp_id': False,'supervisor_id': False,'citymanager_id': False}
        self.isHr = False
        self.user = getCurrentUser()
        
        self.ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
        
    
    def dateValidate(self,date):
        try:
            return datetime.strptime(date,"%Y-%m-%d")
        except:
            return False
    
    def dateTimeValidate(self,date):
        try:
            return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        except:
            return False
            
    def getHierarchy(self,child_user_id):
        
        row = mongo.db.users.find_one({"_id":getId(child_user_id)})
        
        if row:
            if self.user['role'] <= row['role']:
                return False
          
            if str(row['parent_id']) == self.user['user_id']:
                self.__setHierarchy(row['_id'],row['role'])
                self.__setHierarchy(getId(self.user['user_id']),self.user['role'])
              
                
            elif row['parent_id'] is not None:
                self.__setHierarchy(row['_id'],row['role'])
                self.getHierarchy(str(row['parent_id']))
                
            else:
                self.__setHierarchy(row['_id'],row['role'])
            
            if self.isHr:
                return self.hr
            else:
                return False
        else:
            return False
     
    def __setHierarchy(self,user_id,role):
       
        if role == 1:
            self.isHr = True
            self.hr['fwp_id'] = user_id
        elif role == 2:
            self.isHr = True
            self.hr['supervisor_id'] = user_id
        elif role == 3:
            self.isHr = True
            self.hr['citymanager_id'] = user_id
    
    
    def isAssignedOutlet(self,user_id,outlet_id,role=1):
        row = mongo.db.today_outlet.find_one({"outlet_id":getId(outlet_id)})
        
        if row:
            if role == 1 and str(row['fwp_id'] == user_id):
                return True
        return False
                
            
    def userIdValidate(self,user_id):
        try:
            
            row = mongo.db.users.find_one({"_id":getId(user_id)})
            if row:
                return row
            else:
                return False
        
        except:
            return False 
    
    def outletIdValidate(self,outlet_id):
        try:
            result = mongo.db.outlet.find_one({"_id":getId(outlet_id)})
            if not result:
                return False
            return result
        except:
            return False 
        
    
    def fileUpload(self,loc,files):
        if 'file' not in files:
            return False
        file = files['file']
        
        if file.filename == '':
            return False
        
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            unique_filename = str(uuid.uuid4())
            newFilename = unique_filename+"."+str(filename.split(".")[-1])
            
            file.save(os.path.join(app.config['UPLOAD_FOLDER']+loc+"/", newFilename))
            return newFilename;
        
        return False
        
            
    def allowed_file(self,filename):
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
            
            
            
            