from api import app, mongo,jwt
from flask import Flask, jsonify, request
import json
import hashlib 
from api.lib.helper import getData, getId, getCurrentUserId
from bson.int64 import Int64
#from datetime import datetime, date
import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_raw_jwt,fresh_jwt_required,jwt_optional
)


def checkLastLoginAttempt():
    try:
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            ip = request.environ['REMOTE_ADDR']
        else:
            ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
        
        ip = ip.split(',', 1)
        remote_ip = str(ip[0])
        
        dt = datetime.datetime.now()
        
        result = mongo.db.rate_limit.find_one({'remote_ip':remote_ip})
        if result:
            diff = (dt - result['created_at']).total_seconds()
            
            json = {}
            json['attempt'] = result['attempt'] + 1
            json['last_attempt'] = dt
            
            user = mongo.db.rate_limit.update_one({'remote_ip':remote_ip},{"$set":json})
            
            if diff > 60:
                mongo.db.rate_limit.delete_one({'remote_ip':remote_ip})
                json = {}
                json['remote_ip'] = remote_ip
                json['attempt'] = 1
                json['last_attempt'] = dt
                json['created_at'] = dt
                user = mongo.db.rate_limit.insert(json)
            
                return True
            
            if  result['attempt']  > 4 and diff < 60:
                return False
            
        
        else:
            json = {}
            json['remote_ip'] = remote_ip
            json['attempt'] = 1
            json['last_attempt'] = dt
            json['created_at'] = dt
            user = mongo.db.rate_limit.insert(json)
        
    except Exception as e:
        print(e)
        return False



#jwt = JWTManager(app)
blacklist = set()

@jwt.expired_token_loader
def my_expired_token_callback(jwt_header, jwt_payload):
    return jsonify({"msg": "Token has expired"}), 401


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = mongo.db.users.find_one({"_id":getId(identity)})
    return {
        'user_id': identity,
        'role': user['role'],
        'city_id': str(user['city_id'])
    }

@app.route('/login', methods=['POST'])
def login():
    deviceId = request.json.get('deviceId', None)
    firebaseToken = request.json.get('firebaseToken', None)
    
    mobile = request.json.get('mobile', None)
    password = request.json.get('password', None)
    mobile = mobile.replace('"', '')
    user = mongo.db.users.find_one({"mobile":Int64(mobile),"status":1})
    
    
    
    enPass = hashlib.md5(password.encode()).hexdigest()
    #print(user)
    #if mobile != '9999097324' or password != '9999097324':
    if not user or enPass != user['password']:
        r = checkLastLoginAttempt()
        if r == False:
            return jsonify({"msg": "Account has been locked."}),401

        return jsonify({"msg": "Bad Mobile or password"}), 401
    
    if 'isLocked' in user and user['isLocked'] == 1:
        return jsonify({"msg": "Bad Mobile or password"}), 401
    
    user.pop('password') 
    
   
    user = getData(user)
   
  
    if deviceId != None:
        if user['role'] == 5:
            user['role'] = 4
        mongo.db.users.update_one({"_id":getId(user['id'])},{"$set": {'deviceId':deviceId,'firebaseToken':firebaseToken}} )
    
    expires = datetime.timedelta(minutes=60)
    refresh_expires = datetime.timedelta(minutes=1440)
   
    ret = {
        'token': {'access': create_access_token(identity=user['id'],expires_delta=expires),
                  'refresh': create_refresh_token(identity=user['id'],expires_delta=refresh_expires)},
        'profile': user,
    }
   
    return jsonify(ret), 200




@app.route('/isLocked/<id>', methods=['GET'])
def isLocked(id):
    users = mongo.db.users.find({"deviceId":id})
    
    for user in users:
        if 'isLocked' in user and user['isLocked'] == 1: 
            return {'isLocked':1},200
        
    
    return {'isLocked':0},200




@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(minutes=60)
    new_token = create_access_token(identity=current_user,expires_delta=expires, fresh=False)
    ret = {'token':{'access': new_token}}
    return jsonify(ret), 200


@app.route('/logout', methods=['DELETE'])
@jwt_optional
def logout():
    jti = get_raw_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Successfully logged out"}), 200

@app.route('/protected', methods=['GET'])
def protected():
    # ~ app.logger.info('Processing default request')
    username = get_jwt_identity()
    tt = get_raw_jwt()
    return jsonify(logged_in_as=tt), 200



@app.route('/random', methods=['GET'])
def random():
    # ~ app.logger.info('Processing default request')
    return {'status':'ok'},200


