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
"""
import time
import threading

class Test(object):
    def __init__(self, interval=1):
        threadA = threading.Thread(target=self.loop_infinito, args=())
        threadA.daemon = True     
        threadA.start() 
        
    def testing(self):
        print('nada')
    
    def loop_infinito(self):
        while True:
            print('soy un bucle infinito')
            time.sleep(1)

    def threading_loop_infinito(self):
        threadA = threading.Thread(target=self.loop_infinito(), args=())
        threadA.daemon = True     
        threadA.start() 
    
    def loop_infinito_otracosa(self):
        self.threading_loop_infinito()
        #while True:
        #    print('OTRO BUCLE')
        

test = Test()
#test.loop_infinito_otracosa()
time.sleep(3)
print('Checkpoint')
time.sleep(2)
print('Bye')
"""
"""
import threading
import time


class ThreadingExample(object):

    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            # Do something
            print('Doing something imporant in the background')

            time.sleep(self.interval)

example = ThreadingExample()
time.sleep(3)
print('Checkpoint')
time.sleep(2)
print('Bye')
"""


#test svg

#!/usr/bin/env python

# Inspired by https://gist.github.com/jtangelder/e445e9a7f5e31c220be6
# Python3 http.server for Single Page Application

import urllib.parse
import http.server
import socketserver
import re
from pathlib import Path

HOST = ('0.0.0.0', 8000)
pattern = re.compile('.png|.jpg|.jpeg|.js|.css|.ico|.gif|.svg', re.IGNORECASE)


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url_parts = urllib.parse.urlparse(self.path)
        request_file_path = Path(url_parts.path.strip("/"))

        ext = request_file_path.suffix
        if not request_file_path.is_file() and not pattern.match(ext):
            self.path = 'index.html'

        return http.server.SimpleHTTPRequestHandler.do_GET(self)


httpd = socketserver.TCPServer(HOST, Handler)
httpd.serve_forever()
