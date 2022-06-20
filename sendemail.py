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
#Import everything we need
import sys, os
import time
import datetime
import smtplib
import subprocess
#for sending emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
#for getting settings
from parsettings import parsettings
#path to find playouter settings
settings_path = '/home/administrador/.openbroadcaster'

def send_email(message=sys.argv[1]):
    try:
        settings = parsettings(settings_path)
        settings = settings.loadSettings()

        hostname =  subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE)
        hostname = hostname.stdout.read().decode("utf-8").rstrip()

        msg = MIMEMultipart()
        msg['From'] = settings['email_from']
        msg['To'] = str('"'+settings['email_to']+'"')
        msg['Subject'] = "PlayIter Alert " + hostname
        email_to_list = settings['email_to'].split(",")

        body = message
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP(settings['email_server'],settings['email_port'])
        server.starttls()
        server.login(settings['email_user'], settings['email_pass'])
        text = msg.as_string()

        server.sendmail(settings['email_from'], email_to_list, text)
        server.quit()

        print('SEND EMAIL: email has been sent to ' + msg['To'])
    except:
        print('SEND EMAIL: email cannot be send')
send_email()
