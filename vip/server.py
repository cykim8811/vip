from flask import Flask, session, render_template, send_from_directory, redirect, request
from flask_socketio import SocketIO, emit
from importlib_resources import files, as_file

from vip.workspace import *

import os
import json
import logging

default_config = {
    'SECRET_KEY': os.urandom(24).hex(),
    'DEBUG': True,
    'HOST': '127.0.0.1',
    'PORT': 80,
    'PASSWORD': os.urandom(24).hex()    # TODO: Add Hashing to Password
}

class VIP:
    def __init__(self):
        self.config_dir = os.path.expanduser('~') + "/.vip/config.json"
        self.resource_dir = str(files('vip').joinpath("resources/public"))
        self.app = Flask(__name__)
        self.host = "127.0.0.1"
        self.port = 80
        self.password = os.urandom(24).hex()
        
        
        self.workspace = Workspace()
        def sendMsg(data): emit('message', data)
        self.workspace.registerCallback(sendMsg)
        
        self.app.logger.disabled=True
        log = logging.getLogger('werkzeug')
        log.disabled = True

        if os.path.isfile(self.config_dir):
            self.app.config.from_file(self.config_dir, load=json.load)
            with open(self.config_dir, 'r') as f:
                config_json = json.load(f)
                if 'HOST' in config_json: self.host = config_json['HOST']
                if 'PORT' in config_json: self.port = config_json['PORT']
                if 'PASSWORD' in config_json: self.password = config_json['PASSWORD']
        else:
            if not os.path.exists(os.path.expanduser('~')+"/.vip"):
                os.mkdir(os.path.expanduser('~')+"/.vip")
            print("Creating config file to", os.path.expanduser('~') + "/.vip")
            with open(self.config_dir, 'w') as f:
                json.dump(default_config, f)
        self.socketio = SocketIO(self.app)
        
        @self.app.route('/')
        def root():
            if 'authenticated' not in session or not session['authenticated']: # Not Authenticated
                return redirect("/login", 302)
            
            return send_from_directory(self.resource_dir, 'main/index.html')
                
        
        @self.app.route('/public/<path:path>')
        def public(path):
            return send_from_directory(self.resource_dir, path)
        
        @self.app.before_request
        def before_request():
            if 'session' in session and 'authenticated' in session:
                pass
            else:
                session['session'] = os.urandom(24)
                session['authenticated'] = False
                
        @self.app.route('/login')
        def login():
            if self.password == "": session['authenticated'] = True
            if 'authenticated' in session and session['authenticated']: return redirect("/", 302)
            return send_from_directory(self.resource_dir, 'login/index.html')
        
        @self.app.route('/authenticate', methods=['POST'])
        def authenticate():
            recv = request.form['password']
            if self.password == recv:
                session['authenticated'] = True
                return redirect("/", 302)
            else:
                return redirect("/login", 302)
        
        @self.socketio.on('message')
        def message(data):
            if 'authenticated' not in session or not session['authenticated']: return
            self.workspace.onMessage(data)
            
        @self.socketio.on('request_data')
        def req(data):
            if 'authenticated' not in session or not session['authenticated']: return
            emit('response', {'msg_id': data['msg_id'], 'data': self.workspace.onRequest(data['data'])})
            
            
    def addClassFromFile(self, class_ref, template_path):
        self.workspace.addClassFromFile(class_ref, template_path)
            
    def addClassFromString(self, class_ref, template_string):
        self.workspace.addClass(class_ref, template_string)
        
    def addInstance(self, instance):
        self.workspace.addInstance(instance)
        
    def addFunctionFromFile(self, function_ref, template_path):
        self.workspace.addFunctionFromFile(function_ref, template_path)
        
    def addFunctionFromString(self, function_ref, template_string):
        self.workspace.addFunction(function_ref, template_string)
    
    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port)
