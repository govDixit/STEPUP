#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api import app, mongo, socketio
#import api
from api.models import printer
from http import HTTPStatus
from flask import Flask, jsonify, request,abort
from flask_jwt_extended import verify_jwt_in_request,jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime
import gevent.pywsgi

@app.errorhandler(404)
def not_found404(e):
    return jsonify({"error":"The Requested API instance was not found."}),404
 
 
@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error":"Internal Server Error."}),500
  
@app.before_request
def before_request():
    if not (request.endpoint == 'login' or request.endpoint == 'refresh' or request.endpoint == 'isLocked' or request.endpoint == 'assets' 
            or request.endpoint == "reportdownload" or request.endpoint == "learningdownload" 
            or request.endpoint == "skillsdownload" or request.endpoint == "signaturedownload"
            or request.endpoint == "checkindownload"
            or request.endpoint == "userpic"):

        #jwt_required()
        verify_jwt_in_request()
        #return jsonify({"msg": request.endpoint}),200

       
@app.after_request
def after_request(response):
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        ip = request.environ['REMOTE_ADDR']
    else:
        ip = request.environ['HTTP_X_FORWARDED_FOR'] # if behind a proxy
    print(request.endpoint)
    json = {}
    json['user_id'] = get_jwt_identity()
    json['endpoint'] = request.endpoint
    json['uri'] = request.path
    json['method'] = request.method
    json['ip'] = ip
    json['request'] = request.get_json(force=True, silent=True)
    json['response'] = response.get_json()
    json['status'] = response.status_code
    json['created_at'] = datetime.now()
    mongo.db.logs.insert_one(json)
    return response

if __name__=='__main__':
    app_server = gevent.pywsgi.WSGIServer(('0.0.0.0', 5002), app)
    app_server.serve_forever()
