from flask import session, redirect, url_for, render_template, request
from . import main
from .forms import LoginForm
import uuid
import json
from app import mongo

@main.route('/', methods=['GET', 'POST'])
def index():
    
    #if 'logged_in' not in session:
    session['logged_in'] = True
    session['user_id'] = str(uuid.uuid4())
    session['priority'] = 1
    
    return render_template('index.html')




"""@main.route('/import', methods=['GET', 'POST'])
def importFile():
    with open('question.json', 'r') as f:
        array = json.load(f)

    for row in array:
        mongo.db.form_fields.insert(row)
    print(array)
    exit();"""
