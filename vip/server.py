from flask import Flask, session, render_template, send_from_directory, redirect, request
from flask_socketio import SocketIO, emit
from importlib_resources import files, as_file

from vip.workspace import *

import os
import json
import logging

class VIPServer:
    def __init__(self):
        self.resource_dir = str(files('vip').joinpath("resources/public"))
        self.app = Flask(__name__)
        self.app.secret_key = os.urandom(24)
        self.socketio = SocketIO(self.app)
        
        @self.app.route('/')
        def root():
            pass
        
        @self.app.route('/public/<path:path>')
        def public(path):
            return send_from_directory(self.resource_dir, path)
        
        @self.app.before_request
        def before_request():
            if 'session' not in session or 'workspace' not in session:
                session['session'] = os.urandom(24)
                session['workspace'] = VIPWorkspace()
                
        @self.socketio.on('message')
        def message(data):
            pass
            
        @self.socketio.on('request_data')
        def req(data):
            if 'authenticated' not in session or not session['authenticated']: return
            emit('response', {'msg_id': data['msg_id'], 'data': self.workspace.onRequest(data['data'])})
    
    def run(self):
        self.socketio.run(self.app, host='0.0.0.0', port=80)
