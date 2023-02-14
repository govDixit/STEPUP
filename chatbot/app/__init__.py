from flask import Flask
from flask_socketio import SocketIO
from flask_pymongo import PyMongo
#from datetime import datetime
import datetime

socketio = SocketIO(async_mode="threading")
app = Flask(__name__)
#app.debug = True

app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'
app.config["MONGO_URI"] = "mongodb://pmi:Title321@188.166.244.140:27017/pmi-chatbot"

#app.config["SESSION_PERMANENT"] = False
#app.permanent_session_lifetime = False


#app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(minutes=1)

mongo = PyMongo(app)

#result = mongo.db.form_fields.find_one({'priority':1})
#print(result)

def create_app(debug=False):
    """Create an application."""
    
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    return app

