from api import app, mongo
from flask import Flask, jsonify, request
import json
import hashlib 
from api.lib.helper import getData,getId
from bson.int64 import Int64
#from datetime import datetime, date
import datetime
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, get_raw_jwt,fresh_jwt_required,jwt_optional
)


jwt = JWTManager(app)
blacklist = set()

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in blacklist

@jwt.user_claims_loader
def add_claims_to_access_token(identity):
    user = mongo.db.users.find_one({"_id":getId(identity)})
    return {
        'user_id': identity,
        'role': user['role']
    }

@app.route('/login', methods=['POST'])
def login():
    
    mobile = request.json.get('mobile', None)
    password = request.json.get('password', None)
    mobile = mobile.replace('"', '')
    user = mongo.db.users.find_one({"mobile":Int64(mobile)})
    enPass = hashlib.md5(password.encode()).hexdigest()
    #print(user)
    #if mobile != '9999097324' or password != '9999097324':
    if not user or enPass != user['password']:
        return jsonify({"msg": "Bad Mobile or password"}), 401
    user.pop('password') 
    user = getData(user)
  
    expires = datetime.timedelta(minutes=10800)
    refresh_expires = datetime.timedelta(minutes=10800)
    ret = {
        'token': {'access': create_access_token(identity=user['id'],expires_delta=expires),
                  'refresh': create_refresh_token(identity=user['id'],expires_delta=refresh_expires)},
        'profile': user,
    }
    
    return jsonify(ret), 200


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    expires = datetime.timedelta(minutes=10800)
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
    app.logger.info('Processing default request')
    username = get_jwt_identity()
    tt = get_raw_jwt()
    return jsonify(logged_in_as=tt), 200



@app.route('/random', methods=['GET'])
def random():
    app.logger.info('Processing default request')
    return {'status':'ok'},200

