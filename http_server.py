#!/usr/bin/env python
#Sebastian Porteiro 2017-20 seba@sebastianporteiro.com
import sys, os
import gi
import subprocess
gi.require_version('Gst', '1.0')
gi.require_version('Gtk', '3.0')
gi.require_version('GstVideo', '1.0')
from gi.repository import GObject, Gst, Gtk, Gdk
from gi.repository import GdkX11, GstVideo
import time
import datetime
import configparser
import threading
import json
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer

from pipes import Pipes
from parsettings import parsettings
from mixter import Mixter

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 8066
NOW = datetime.datetime.now().strftime("%Y%m%d")
SALT = str('9df3e8281eb7cc58472991635a9e7e62d614f688c018eaa1cf376192' + str(NOW))
TOKEN = hashlib.sha224(SALT.encode('UTF-8')).hexdigest()

MIXTER = Mixter()
threadA = threading.Thread(target=MIXTER.be_loop, args=())
threadA.setDaemon(True)
threadA.start() 

class http_server(BaseHTTPRequestHandler):
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        paths = {
            '/savesettings': {'status': 200,'Content-type':'text/html'},
            '/login': {'status': 200,'Content-type':'text/html'},
        }
        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500,'Content-type':'text/html'})

    def do_GET(self):
        paths = {
            '/': {'status': 200,'Content-type':'text/html'},
            '/log': {'status': 200,'Content-type':'text/html'},
            '/checkpipeline': {'status': 200,'Content-type':'text/html'},
            '/mixter_status.json': {'status': 200,'Content-type':'text/html'},
            '/settings': {'status': 200,'Content-type':'text/html'},
            '/VERSION': {'status': 200,'Content-type':'text/html'},
            '/get_pipelines': {'status': 200,'Content-type':'text/html'},
            '/datetime': {'status': 200,'Content-type':'text/html'}
        }
        if self.path.endswith(".ico"):
            self.respond({'status': 200,'Content-type':'image/x-icon'})
        elif self.path.endswith(".css"):
            self.respond({'status': 200,'Content-type':'text/css'})
        elif self.path.endswith(".ttf"):
            self.respond({'status': 200,'Content-type':'application/x-font-ttf'})
        elif self.path.endswith(".svg"):
            self.respond({'status': 200,'Content-type':'image/svg+xml'})
        elif self.path.endswith(".png"):
            self.respond({'status': 200,'Content-type':'image/png'})
        elif self.path.endswith(".jpg"):
            self.respond({'status': 200,'Content-type':'image/jpg'})
        elif self.path.endswith(".css"):
            self.respond({'status': 200,'Content-type':'text/css'})
        elif self.path.endswith(".js"):
            self.respond({'status': 200,'Content-type':'text/javascript'})
        elif self.path.endswith(".json"):
            self.respond({'status': 200,'Content-type':'application/json'})
        elif self.path.endswith(".log"):
            self.respond({'status': 200,'Content-type':'text/html'})
        elif self.path.endswith(".html"):
            self.respond({'status': 200,'Content-type':'text/html'})
        elif self.path.endswith(TOKEN):
            self.respond({'status': 200,'Content-type':'text/html'})

        else:
            if self.path in paths:
                #print(self.path)
                self.respond(paths[self.path])
            else:
                self.respond({'status': 500,'Content-type':'text/html'})

    def handle_http(self, status_code, path):
        self.parsettings = parsettings(MIXTER.mixter_settings_path)
        self.send_response(status_code)
        #serve html files
        #this one should not be
        
        f = open(self.get_path() + '/html/login.html','r')
        contents = f.read()
        f.close()

        if path == '/':
            f = open(self.get_path() + '/html/login.html','r')
            contents = f.read()
            f.close()

        elif path == '/index?'+str(TOKEN):
            f = open(self.get_path() + '/html/index.html','r')
            contents = f.read()
            f.close()

        elif path == '/settingshtml?'+str(TOKEN):
            f = open(self.get_path() + '/html/settings.html','r')
            contents = f.read()
            f.close()

        #call methods of mixter

        elif path == '/buildpipeline':
            MIXTER.build_pipeline()
            contents='{"Pipeline":"Building"}'

        elif path == '/reconnect':
            MIXTER.reconnect()

        elif path == '/disconnect':
            MIXTER.disconnect(1)

        elif path == '/flush':
            MIXTER.flush(1)

        elif path == '/log':
            f = open(MIXTER.loaded_settings['log_path'] + '/mixter.log','r')
            contents = f.read()
            f.close()

        elif path == '/settings':
            contents =  json.dumps(self.parsettings.loadSettings())

        elif path == '/reload':
            MIXTER.load_settings()
            #MIXTER.reconnect()

        elif path == '/toggle_overlay':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            imgdata = str(post_body.decode('UTF-8'))
            MIXTER.toggle_overlay(imgdata)

        elif path == '/toggle_textoverlay':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            string = str(post_body.decode('UTF-8'))
            MIXTER.toggle_textoverlay(string)

        elif path == '/get_pipelines':
            contents =  json.dumps(MIXTER.get_pipelines())

        elif path == '/kill_pipeline':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            pipeline_number = str(post_body.decode('UTF-8'))
            contents =  json.dumps(MIXTER.kill_pipeline(int(pipeline_number)))

        #other methods
        elif self.path == "/VERSION":
            return self.get_file('rb')

        elif self.path == "/datetime":
            contents = str(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))


        #serve any file with this extension
        elif self.path.endswith(".js"):
            contents = self.get_file()

        elif self.path.endswith(".css"):
            contents = self.get_file()

        elif self.path.endswith(".svg"):
            contents = self.get_file()

        elif self.path.endswith(".json"):
            contents = self.get_file()

        elif self.path.endswith(".log"):
            contents = self.get_file()

        elif self.path.endswith(".ico"):
            return self.get_file('rb')

        elif self.path.endswith(".ttf"):
            #in case of ttf dont return bytes
            return self.get_file('rb')

        elif self.path.endswith(".png"):
            #in case of png dont return bytes
            return self.get_file('rb')

        elif self.path.endswith(".jpg"):
            #in case of jpg dont return bytes
            return self.get_file('rb')

#################################	
# POST              			#
#		                		#
#################################

        elif path == '/savesettings':
            print(self.headers)
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            settings = post_body.decode('UTF-8')
            settings = json.loads(settings)
            self.parsettings.saveSettings(settings)
            print(settings)
            contents='HTTP MIXTER RESPONSE: Settings saved succesfully'

        elif path == '/login':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            data = post_body.decode('UTF-8')
            data = json.loads(data)
            userAndPassword = str(data['login_username']+data['login_password'])
            userAndPassword = userAndPassword.encode('utf8')
            userAndPassword = hashlib.sha224(userAndPassword).hexdigest()
            token_given = str(str(userAndPassword) + str(NOW))
            token_given = hashlib.sha224(token_given.encode('UTF-8')).hexdigest()

            if token_given == TOKEN:
                contents = str(TOKEN)
            else:
                contents = '403'
        return bytes(contents, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-type',opts['Content-type'])
        self.end_headers()
        self.wfile.write(response)

    def get_file(self,read_mode='r'):
        try:
            f = open(str(self.get_path()+self.path),read_mode)
            contents = f.read()
            f.close()
            return contents
        except:
            print('HTTP MIXTER RESPONSE: Cannot load content ' + self.get_path()+self.path)
            return 'HTTP MIXTER RESPONSE: Cannot load content'

    def get_path(self):
        return os.path.dirname(os.path.realpath(__file__))


if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), http_server)
    print('['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']', 'HTTP MIXTER RESPONSE: Web server listening - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']', 'HTTP MIXTER RESPONSE: Web server stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
