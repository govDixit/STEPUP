from api import app
from api import Api
from api.models import Printer
from flask import render_template
from flask import Flask, jsonify, request
#import api.controller.printer
#import api.controller.outlet
#import api.controller.auth
from api.controller import auth,user,city,attendance
from api.controller import outlet,outletCheckin,outletBreak
from api.controller import miForm,FormField, stock,stockVerification,product

from api.controller import fwpStatics

from api.controller import outletWebActivity, formNotification, outletNotification

from api.controller import chatUser

from api.controller import sos, skills, learning, filter, reports, calender, webGraph

from api.controller import questions, broadcast

import api.controller.graph

import api.controller.cityWDArea
