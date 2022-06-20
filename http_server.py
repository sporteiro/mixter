#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#Sebastian Porteiro 2017-2022 seba@sebastianporteiro.com
"""
Copyright 2017-2022 Sebastian Porteiro

This file is part of Mixter.

Mixter is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Mixter is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with Mixter.  If not, see <http://www.gnu.org/licenses/>.
"""

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
import smtplib
import threading
import json
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from http.server import BaseHTTPRequestHandler, HTTPServer
#importar las demas clases de archivos
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
            '/suicide': {'status': 200,'Content-type':'text/html'}
        }
        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500,'Content-type':'text/html'})

    def do_GET(self):
        paths = {
            '/': {'status': 200,'Content-type':'text/html'},
            '/log': {'status': 200,'Content-type':'text/html'},
            '/checkobplayer': {'status': 200,'Content-type':'text/html'},
            '/checksnowmix': {'status': 200,'Content-type':'text/html'},
            '/checkbrave': {'status': 200,'Content-type':'text/html'},
            '/checkpipeline': {'status': 200,'Content-type':'text/html'},
            '/mixter_status.json': {'status': 200,'Content-type':'text/html'},
            '/settings': {'status': 200,'Content-type':'text/html'},
            '/checkram': {'status': 200,'Content-type':'text/html'},
            '/VERSION': {'status': 200,'Content-type':'text/html'},
            '/get_pipelines': {'status': 200,'Content-type':'text/html'},
            '/pipelineform': {'status': 200,'Content-type':'text/html'},
            '/datetime': {'status': 200,'Content-type':'text/html'},
            '/buildpipeline': {'status': 200,'Content-type':'text/html'}
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
        elif self.path.endswith(".dot"):
            self.respond({'status': 200,'Content-type':'application/msword'})
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
                self.respond(paths[self.path])
            else:
                self.respond({'status': 500,'Content-type':'text/html'})

    def handle_http(self, status_code, path):
        self.parsettings = parsettings(MIXTER.mixter_settings_path)
        self.send_response(status_code)
        #serve html files
        #this one should not be
        
        f = open(self.get_path() + '/html/login.html','r',encoding='utf8')
        contents = f.read()
        f.close()

        if path == '/':
            f = open(self.get_path() + '/html/login.html','r',encoding='utf8')
            contents = f.read()
            f.close()

        elif path == '/index?'+str(TOKEN):
            f = open(self.get_path() + '/html/index.html','r',encoding='utf8')
            contents = f.read()
            f.close()

        elif path == '/settingshtml?'+str(TOKEN):
            f = open(self.get_path() + '/html/settings.html','r',encoding='utf8')
            contents = f.read()
            f.close()

        elif path == '/statushtml?'+str(TOKEN):
            f = open(self.get_path() + '/html/status.html','r',encoding='utf8')
            contents = f.read()
            f.close()

        elif path == '/scheme':
            f = open(self.get_path() + '/html/status.html','r',encoding='utf8')
            contents = f.read()
            f.close()

        #call methods of mixter
        elif path == '/checkobplayer':
            MIXTER.check_process('obplayer')
            contents='{"obplayer":"'+str(MIXTER.check_process('obplayer'))+'"}'

        elif path == '/checksnowmix':
            contents='{"snowmix":"'+str(MIXTER.check_process('snowmix'))+'"}'

        elif path == '/checkbrave':
            contents='{"brave":"'+str(MIXTER.check_process('brave'))+'"}'

        elif path == '/checkpipeline':
            contents='{"play":"'+str(MIXTER.check_pipeline_status())+'"}'

        elif path == '/checkram':
            contents='{"RAM":"'+str(MIXTER.check_ram())+'"}'

        elif path == '/buildpipeline':
            pipeline_text=''
            pipeline_settings=''
            try:
                length = int(self.headers.get('content-length'))
                post_body = self.rfile.read(length)
                try:
                    pipeline_settings = json.loads(post_body.decode('UTF-8'))
                except:
                    pipeline_text = str(post_body.decode('UTF-8'))
            except:
                pass

            if pipeline_text !='' or pipeline_settings!='':
                MIXTER.build_pipeline(pipeline_text,pipeline_settings)
                contents='{"Pipeline":"Building "'+pipeline_text+ ' ' +str(pipeline_settings)+'}'
            else:
                MIXTER.build_pipeline()
                contents='{"Pipeline":"Building"}'


        elif path == '/buildmultiplepipelines':
            MIXTER.build_multiple_pipelines()
            contents='{"Pipeline":"Building Multiple Pipelines"}'

        elif path == '/launchobplayer': 
            #self.parsettings.saveSettings({'input_type':'obplayer','brave':'Off','obplayer':'On'})
            MIXTER.execute_program('obplayer')

        elif path == '/launchsnowmix': 
            MIXTER.execute_program('snowmix')

        elif path == '/reconnect':
            MIXTER.reconnect()

        elif path == '/restart_brave':
            MIXTER.restart_brave()

        elif path == '/killall':
            MIXTER.kill_all(1)

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

        elif path == '/restart':
            MIXTER.clean_kill_and_restart()

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

        elif path == '/kill_all_pipelines':
            contents =  json.dumps(MIXTER.kill_all_pipelines())

        elif path == '/reconnect':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            pipeline_number = str(post_body.decode('UTF-8'))
            contents =  json.dumps(MIXTER.reconnect(int(pipeline_number)))

        #settings presets
        elif path == '/preset_tdt_brave':
            self.parsettings.saveSettings({'input_type':'shm_src','brave':'On','obplayer':'On','output_type':'tcp_udp_ffmpeg','video_format':'RGBx','audio_src':'/tmp/brave_audio','video_src':'/tmp/brave_video'})
            MIXTER.load_settings()
            #MIXTER.build_pipeline()

        elif path == '/preset_tdt_obplayer':
            self.parsettings.saveSettings({'input_type':'shm_src','brave':'Off','obplayer':'On','output_type':'tcp_udp_ffmpeg','video_format':'BGRA','audio_src':'/tmp/audio','video_src':'/tmp/video'})
            MIXTER.load_settings()

        elif path == '/preset_legalcopy':
            self.parsettings.saveSettings({'input_type':'udp','brave':'Off','obplayer':'Off','output_type':'file','video_format':'BGRA','file_bitrate':'512','file_duration':'86400000000000','file_tmp_path':'/tmp/tmp_video_%1d.ts','file_path':'/tmp/'})
            MIXTER.load_settings()

        #other methods
        elif self.path == "/VERSION":
            return self.get_file('rb')

        elif self.path == "/datetime":
            contents = str(datetime.datetime.now().strftime("%Y%m%d %H:%M:%S"))


        #serve any file with this extension
        elif self.path.endswith(".js"):
            contents = self.get_file('r','utf8')

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

        elif self.path.endswith(".dot"):
            #in case of png dont return bytes
            return self.get_file('rb')

        elif self.path.endswith(".jpg"):
            #in case of jpg dont return bytes
            return self.get_file('rb')

        elif self.path.endswith(".html"):
            contents = self.get_file('r','utf8')

#################################	
# POST              			#
#		                		#
#################################

        elif path == '/sendmail':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            msg = str(post_body.decode('UTF-8'))
            MIXTER.send_email(msg)
            contents='HTTP MIXTER RESPONSE: email has been sent'


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

        elif path == '/suicide':
            length = int(self.headers.get('content-length'))
            post_body = self.rfile.read(length)
            data = post_body.decode('UTF-8')
            data = json.loads(data)
            token_received = str(data['token'])
            print(TOKEN)
            if token_received==TOKEN:
            #killall tail does not work if we are not root 
                print('HTTP MIXTER RESPONSE: Suicide! **********************************')
                MIXTER.send_email('HTTP\ MIXTER\ WARNING:\ Intento\ de\ suicidio\ manual')
                MIXTER.send_telegram_msg('HTTP MIXTER WARNING: Intento de suicidio manual')
                subprocess.Popen("curl -X POST -d '{\"user\":admin\",\"pass\":\"admin\"}'  http://localhost:1666/suicide;killall tail", shell=True, stdout=subprocess.PIPE)
                MIXTER.clean_kill_and_restart()
                sys.exit()
            else:
                contents = 'HTTP MIXTER RESPONSE: Authentication failure'

        return bytes(contents, 'UTF-8')



    def respond(self, opts):

        response = self.handle_http(opts['status'], self.path)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-type',opts['Content-type'])
        self.end_headers()
        self.wfile.write(response)

    def get_file(self,read_mode='r',encoder=False):
        try:
            if encoder:
                f = open(str(self.get_path()+self.path),read_mode,encoding=encoder)
            else:
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
