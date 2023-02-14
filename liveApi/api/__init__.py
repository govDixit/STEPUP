# -*- coding: utf-8 -*-

__version__ = '0.1'

from flask import Flask
from flask_restful import Resource, Api
from flask_pymongo import PyMongo
from api.lib.mongoflask import *
from flask_cors import CORS,cross_origin
import datetime
import logging
from flask_json import FlaskJSON, JsonError, json_response, as_json
from werkzeug.utils import secure_filename

from flask_socketio import SocketIO
import os
from flask_jwt_extended import JWTManager

app = Flask('api')

CORS(app, support_credentials=True,resources={r"*": {"origins": "https://www.stepupforward.com"}})

#logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(filename='app.log', level=logging.DEBUG)

inv = 'test'
inv = 'live'
#inv = 'local'

app.config['SECRET_KEY'] ='PMA-Nb?GzJa6P6tN*66&Nb?GzJa6P6tN*66&Nb?GzJa6P6tN*66&'


if inv == 'live':
    app.config["MONGO_URI"] = "mongodb://pmi:Title321@127.0.0.1:27017/pmi"
    app.config['REPORT_URL'] = "https://www.stepupforward.com/api/report/download/"
    app.config['DOC_URL'] = "https://www.stepupforward.com/api/"
elif inv == 'test':
    app.config["MONGO_URI"] = "mongodb://pmi:Title321@127.0.0.1:27017/pmi_test"
    app.config['REPORT_URL'] = "http://stepupforward.com/api/test/report/download/"
    app.config['DOC_URL'] = "http://stepupforward.com/api/test/"
else:
    app.config["MONGO_URI"] = "mongodb://pmi:Title321@188.166.244.140:27017/pmi"
    app.config['REPORT_URL'] = "http://localhost:5000/report/download/"
    app.config['DOC_URL'] = "http://localhost:5000/"




app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['JWT_SECRET_KEY'] = 'PMISecretKey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(minutes=15)
app.config['JWT_BLACKLIST_ENABLED'] = True

app.config['BASE_URL'] = "https://www.stepupforward.com/assets/default/"




UPLOAD_FOLDER = 'uploads/'

app.config['UPLOAD_FOLDER'] = os.path.join(UPLOAD_FOLDER)

apiV1 = Api(app)
mongo = PyMongo(app)
jwt = JWTManager(app)


socketio = SocketIO(async_mode="threading")
#socketio.init_app(app)


import api.models
import api.controller



