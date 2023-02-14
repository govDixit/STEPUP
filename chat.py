#!/bin/env python
from api import app, mongo, socketio

import api.controller.chatEvents
import api.controller.auth
 
                           
if __name__ == '__main__':
    
    app.config['CORS_SUPPORTS_CREDENTIALS'] = True
    app.config['JWT_TOKEN_LOCATION'] = 'query_string'
    app.config['JWT_QUERY_STRING_NAME'] = 'token'
    
    socketio.init_app(app, cors_allowed_origins="*",ping_interval=30,ping_timeout=60)
    socketio.run(app,host="0.0.0.0",port=5000)
