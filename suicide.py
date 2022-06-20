#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
#Importar todo lo que hace falta
import sys, os
import gi
import subprocess
import time
import datetime
import threading
import json
import hashlib
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 1666
TOKEN = 'a6747e6d9aaa9d5d2e9f172df3e08a1b9bd56dc159b7cb9d72e457f6'

class httpPlayiter(BaseHTTPRequestHandler):
    def do_POST(self):
        paths = {
            '/suicide': {'status': 200,'Content-type':'text/html'}
        }
        if self.path in paths:
            self.respond(paths[self.path])
        else:
            self.respond({'status': 500,'Content-type':'text/html'})

    def handle_http(self, status_code, path):
        self.send_response(status_code)

#################################	
# POST              			#
#		                		#
#################################
        #should be call like curl -X POST -d '{"user":"admin","pass":"admin"}'  http://192.168.53.39:6666/suicide
        if path == '/suicide':
            #print(self.headers)
            try:
                length = int(self.headers.get('content-length'))
                post_body = self.rfile.read(length)
                post_body = post_body.decode('UTF-8')
                post_body = json.loads(post_body)
                userAndPassword = str(post_body['user']+post_body['pass'])
                userAndPassword = userAndPassword.encode('utf8')
                userAndPassword = hashlib.sha224(userAndPassword).hexdigest()
                if userAndPassword == TOKEN:
                    kill_tail = subprocess.Popen("killall tail", shell=True, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                    kill_tail = kill_tail.stderr.read().decode('UTF-8')
                    print(kill_tail)
                    if kill_tail == '':
                        contents = 'Suiciding'
                    else:
                        contents = 'Unable to process, check user and pass or suicide not available'
                else:
                    contents = 'Not Authorized'
            except:
                print('Unable to process, check user and pass or suicide not available')
                contents = 'Unable to process, check user and pass or suicide not available'

        return bytes(contents, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.send_header('Content-type',opts['Content-type'])
        self.end_headers()
        self.wfile.write(response)

    def get_path(self):
        return os.path.dirname(os.path.realpath(__file__))

    def test(self):
        print('Test')
        try:
            print('Test' + self.nada)
        except:
            pass

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), httpPlayiter)
    print('['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']', 'Web server listening - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']', 'Web server stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
