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
#for post requests
import requests
#for sending emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Classes in different files
from pipes import Pipes
from parsettings import parsettings
from continuity import Continuity

#overlays
import json
import cairo
gi.require_foreign('cairo')
#Define this as a constant because it is needed before loading itself

SETTINGS_PATH = '/home/administrador/.openbroadcaster/'
#SETTINGS_PATH = '/home/administrador/mixter/'
#SETTINGS_PATH = '/media/sporteiro/Seba/ITER/desarrollo/mixter/local_settings'

class Mixter(object):
	def __init__(self):
		print("*******MIXTER LOG: Lanzando Mixter*******")
		#Mixter path, useful for saving log or settings
		self.mixter_path=os.path.dirname(os.path.realpath(__file__))
		#self.log_path=self.mixter_path+'/mixter.log'
		self.log_window_message = ''

		#host name, so we can identify it like in sending email alerts
		hostname =  subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE)
		self.hostname = hostname.stdout.read().decode("utf-8").rstrip()
		#print(self.hostname)
		#array of processes so we can check them
		self.processes=[]
		#FIXME is this necessary?
		#contador de errores. puede ser util para desactivar elementos despues de varios intentos, como RTMP, snowmix, etc
		self.total_errors=0
		#settings path, this cannot be in settings file, otherwise we would never call him
		#self.mixter_settings_path = self.mixter_path
		self.mixter_settings_path = SETTINGS_PATH
		#FIXME is this necessary?
		#TODO hace falta? 
		self.ffmpeg_pid = 0 
		self.snowmix_proc = 'Off'
		#Pipeline is None when we start
		self.pipeline = None
		self.gst_pipeline_state = 'NULL'
		#load settings
		self.load_settings()
		self.pipeline_number = 0
		self.pipelines = {}
		self.pipelines_desc = {}
		self.busses = {}
		#delete all graphs, .dot and .png from folder
		subprocess.call('rm -rf '+self.loaded_settings['gst_graph_path']+'*.dot ' +self.loaded_settings['gst_graph_path']+'*.png', shell=True)
		print('delete ' + self.loaded_settings['gst_graph_path']+'*.dot')        
		#only after we have the settings we can try to launch pipeline
		self.launch_pipeline()


#################################	
# Settings						#
#								#
#################################
	def load_settings(self):
		try:
			self.parsettings = parsettings(self.mixter_settings_path)
			self.loaded_settings = self.parsettings.loadSettings()
			self.log_message('[DEBUG] Configuraciones cargadas')
		except:
			print("MIXTER LOG: ERROR, no se pudo cargar el archivo de configuracion o se cargo con errores")
			self.log_message('[ERROR] no se pudo cargar el archivo de configuracion o se cargo con errores')

		#activate gstreamer graphs
		os.environ["GST_DEBUG_DUMP_DOT_DIR"] = self.loaded_settings['gst_graph_path']
		print("MIXTER LOG: DEBUG, GST_DEBUG_DUMP_DOT_DIR : " + os.environ['GST_DEBUG_DUMP_DOT_DIR'])
		self.log_message('[DEBUG] GST_DEBUG_DUMP_DOT_DIR : ' + os.environ['GST_DEBUG_DUMP_DOT_DIR'])


#################################	
# Check external programs		#
#								#
#################################
	def launch_pipeline(self):
		#After settings are loaded, if auto_launch is On, we build gstreamer pipeline
		if self.loaded_settings['auto_launch']=='On':
			#before we launch gstreamer, we need to check additional applications, if they are On, like obplayer, brave
			self.log_message("[DEBUG] Auto_launch activo, se intentara lanzar tuberia")
			programs_to_launch={}
			if self.loaded_settings['obplayer'] == 'On':
				programs_to_launch = ['obplayer']
			if self.loaded_settings['snowmix'] == 'On':
				programs_to_launch.extend(['snowmix'])
			if self.loaded_settings['brave'] == 'On':
				programs_to_launch.extend(['brave'])

			if len(programs_to_launch)!=0:
				self.log_message("[DEBUG] Se intentara lanzar " + str(programs_to_launch))
				if self.launch_secondary_programs(programs_to_launch):
					print("MIXTER LOG: Lanzados programas secundarios")
					self.log_message("[DEBUG] Lanzados programas secundarios")
					#FIXME do we want to check on them ?
					#self.check_input_and_build_pipeline()
					self.build_multiple_pipelines()

			else:
				self.build_multiple_pipelines()
				#self.reconnect()

		else:
			self.log_message("[DEBUG] Auto_launch desactivado, lanzar a mano")
	
	#Launch external programs
	def launch_secondary_programs(self,programs_to_launch):
		programs_checked = len(programs_to_launch)
		all_programs_checked = True
		
		for p in programs_to_launch:
			all_programs_checked = all_programs_checked and self.try_execute_program(p,5)
			#always restart brave the first time ?
		return all_programs_checked

	def try_execute_program(self,p,counter=5):
		if not self.check_process(p) and counter > 0:
			print("MIXTER LOG: Intentando lanzar " + p)
			self.log_message('[DEBUG]  Intentando lanzar ' + p)
			self.execute_program(p)
			#FIXME sleep here is because process can exist, but the program is not yet sending streaming, we need to check when streaming is ok
			time.sleep(3)
			if not self.check_process(p):
				counter -= 1
				self.try_execute_program(p,counter)
				return False
		return True



#################################	
# GSTREAMER build Pipelines 	#
#								#
#################################
	def build_multiple_pipelines(self):
		pipeline_list = json.loads(self.loaded_settings['pipeline_list'])
		#order matters
		pipeline_list_sorted = {}
		keys_sorted = sorted(pipeline_list)
		for n in pipeline_list:
			pipeline_list_sorted[n]=pipeline_list[n]

		for n in  pipeline_list_sorted:
			#print(pipeline_list[n])
			print('MIXTER LOG: Building multiple pipelines')
			self.log_message('[DEBUG] Building multiple pipelines')
			print('MIXTER LOG: Calling build_pipeline with: ' + str(pipeline_list_sorted[n]))
			#self.load_settings()
			#self.parsettings = parsettings(self.mixter_settings_path)
			#self.parsettings.saveSettings(pipeline_list[n])
			#self.load_settings()
			self.build_pipeline('',pipeline_list_sorted[n])

	def build_pipeline(self,pipeline_text='',pipeline_settings=''):
		pipes = Pipes()

		if pipeline_text=='':
			if pipeline_settings=='':
				pipeline_settings = self.loaded_settings

		pipeline_number = self.pipeline_number
		self.pipelines_desc[pipeline_number] = {}
		self.pipelines_desc[pipeline_number]['pipeline_id'] = 'p_'+str(self.pipeline_number)


		if 'pipeline_type' in pipeline_settings and pipeline_settings['pipeline_type']=='ffmpeg':
			if not 'service_name' in pipeline_settings:
				pipeline_settings['service_name'] = 'Mixter service'
			self.ffmpeg_launch(pipes.ffmpeg_pipeline(pipeline_settings))
			self.pipelines_desc[pipeline_number]['pipeline_text'] = str(pipes.ffmpeg_pipeline(pipeline_settings))
			self.pipelines_desc[pipeline_number]['pipeline_settings'] = pipeline_settings
			self.pipelines_desc[pipeline_number]['pid'] = self.ffmpeg_pid

		else:
			if pipeline_text=='':
				if pipeline_settings['output_type']=='shm_sink' and pipeline_settings['input_1_type']=='shm_1_src':
					#FIXME when we lauch a pipeline not using gst.parse.launch we still need to control it
					print('launched continuity.py from http_server')
					self.CONTINUITY = Continuity()
					self.pill2kill = threading.Event()
					self.threadCA = threading.Thread(target=self.CONTINUITY.main, args=(pipeline_settings,))
					self.threadCA.setDaemon(False)
					self.threadCA.start()
					self.pipelines_desc[pipeline_number]['pipeline_settings'] = {"pipeline_name":"CONTINUITY","input_1_type":"shm_1_src","output_type":"shm_sink","input_2_type": "none_2_src","pipeline_type": "gstreamer","video_sink": pipeline_settings['video_sink'], "audio_sink":pipeline_settings['audio_sink'],"color_format_sink":pipeline_settings['color_format_sink']}
				else:
					self.pipelines[pipeline_number] = Gst.parse_launch(pipes.pipe_to_launch(pipeline_settings))
					self.pipelines_desc[pipeline_number]['pipeline_text'] = str(pipes.pipe_to_launch(pipeline_settings))
					self.pipelines_desc[pipeline_number]['pipeline_settings'] = pipeline_settings or self.settings_string_to_array(pipes.get_settings_needed())
					self.connect_bus(pipeline_number)
				print("MIXTER LOG: Lanzando desde: " + pipeline_settings['input_1_type'] + " hasta: " + pipeline_settings['output_type'])
				self.log_message('[DEBUG] Lanzando desde: ' + pipeline_settings['input_1_type'] + " hasta: " + pipeline_settings['output_type'])
			else:
				self.pipelines[pipeline_number] = Gst.parse_launch(pipeline_text)
				self.pipelines_desc[pipeline_number]['pipeline_text'] = str(pipeline_text)
				if pipeline_settings=='':
					self.pipelines_desc[pipeline_number]['pipeline_settings'] = {"pipeline_name":"from text","input_1_type":"unknown","output_type":"unknown"}
				else:
					self.pipelines_desc[pipeline_number]['pipeline_settings'] = pipeline_settings
				self.connect_bus(pipeline_number)


		self.pipeline_number += 1

	def connect_bus(self,pipeline_number):
		#Lanzar la tuberia y conectarse al bus
		self.busses[pipeline_number] = self.pipelines[pipeline_number].get_bus()
		self.busses[pipeline_number].add_signal_watch()
		self.busses[pipeline_number].enable_sync_message_emission()
		self.busses[pipeline_number].connect("message", self.on_message, pipeline_number)
		self.busses[pipeline_number].connect("sync-message::element", self.on_sync_message)
		self.busses[pipeline_number].connect("sync-message::stream-status", self.on_stream_message)

		self.pipelines[pipeline_number].set_name('p_'+str(self.pipeline_number))
		print('MIXTER LOG: Tuberia construida, bus conectado')
		self.log_message('[DEBUG] Pipeline: Tuberia construida, bus conectado ' + str(self.pipelines[pipeline_number].get_name()))	
		#latencia 
		self.latency = self.pipelines[pipeline_number].get_latency()
		print('MIXTER LOG: Latencia ' + str(self.latency))

		self.pipelines[pipeline_number].set_state(Gst.State.PLAYING)
		#TODO this is not the best way to check pipeline state
		self.gst_pipeline_state = 'PLAYING'
		print('MIXTER LOG: GST state ' + self.gst_pipeline_state)
		self.log_message('[DEBUG] GST state ' + self.gst_pipeline_state)

		#self.pipelines_desc[pipeline_number]['pipeline_id'] = str(self.pipelines[pipeline_number].get_name())

		#self.pipelines_desc[pipeline_number]['pipeline_settings_used'] = pipeline_settings or self.settings_string_to_array(pipes.get_settings_needed())
		#gstreamer graphs
		Gst.debug_bin_to_dot_file(self.pipelines[pipeline_number],Gst.DebugGraphDetails(15),self.pipelines_desc[pipeline_number]['pipeline_id'])
		self.dot_to_png(self.pipelines_desc[pipeline_number]['pipeline_id'])


	def ffmpeg_launch(self,ffmpeg_pipeline):
		print(' ffmpeg_pipeline: ' +str(ffmpeg_pipeline))
		#self.kill_ffmpeg()
		ffmpeg_tcp = subprocess.Popen(self.loaded_settings['ffmpeg_path']+"/ffmpeg "+ffmpeg_pipeline, shell=True, stdout=subprocess.PIPE)
		self.ffmpeg_pid=int(ffmpeg_tcp.pid)						
		print("MIXTER LOG: UDP streaming with FFMPEG PID "+str(self.ffmpeg_pid))
		self.log_message('[DEBUG] UDP streaming with FFMPEG PID '+str(self.ffmpeg_pid))


#################################	
# Overlay						#
#								#
#################################

	def toggle_overlay(self,imgdata):
		#self.load_settings()
		data = json.loads(imgdata)
		pipeline_number = int(data['pipeline_number'])
		overlay_id = str(data['id'])
		overlay_src = str(data['src'])
		svgoverlay = self.pipelines[pipeline_number].get_by_name('svgoverlay'+overlay_id)
		svgoverlay.set_property('location', overlay_src)

	def toggle_textoverlay(self,string):
		#self.load_settings()
		#textoverlay.connect('draw', self.on_draw,string)
		self.cairotextstring = str(string)
		#data = string.decode('UTF-8')
		data = json.loads(string)
		self.cairotextstring = str(data['string'])
		self.cairotextmove_to_x = int(data['move_to_x'])
		self.cairotextmove_to_y = int(data['move_to_y'])
		self.cairotextfont_size = int(data['font_size'])

		pipeline_number = int(data['pipeline_number'])
		textoverlay = self.pipelines[pipeline_number].get_by_name('textoverlay')
		textoverlay.connect('draw', self.on_draw)


	def on_draw(self, _overlay, context, _timestamp, _duration):
		"""Each time the 'draw' signal is emitted"""
		context.select_font_face('Open Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
		context.set_font_size(self.cairotextfont_size)
		context.move_to(self.cairotextmove_to_x,self.cairotextmove_to_y)
		context.text_path(self.cairotextstring)
		context.set_source_rgb(1, 1, 1)
		context.fill_preserve()
		context.set_source_rgb(0, 0, 0)
		context.set_line_width(1)
		context.stroke()


#################################	
# GST-messages					#
#								#
#################################
	def on_message(self, bus, message, pipeline_number):
		#print("MIXTER LOG message: Mensaje de GST recibido")
		t = message.type
		if t == Gst.MessageType.EOS:
			self.log_message("[ERROR] EOS from pipeline_"+ str(pipeline_number))	
			self.reconnect(pipeline_number)
		elif t == Gst.MessageType.ERROR:
			self.reconnect(pipeline_number)
			err, debug = message.parse_error()
			error="Error: %s" % err, debug
			print("MIXTER LOG message: Error:" + str(error))
			self.log_message("[ERROR] from pipeline_"+ str(pipeline_number)+' '+ str(error))
			self.handle_msg(debug)
			
		elif t == Gst.MessageType.BUFFERING:
			percent = message.parse_buffering()
			if percent > 60:
				print("MIXTER LOG message: Porcentaje de buffering (imprimir solo mas de 60%): " + str(percent))
				self.log_message("[BUFFER] Porcentaje: "+ str(percent))	
		
		elif t == Gst.MessageType.ELEMENT:
			msg = message.get_structure()
			msgstr=str(msg.get_name())
			#Recibir mensaje cada vez que se genera un nuevo fichero (cuando finaliza la escritura)
			if msgstr=="GstMultiFileSink":	
				print("MIXTER LOG: Nuevo fichero")
				filename=(message.get_structure().get_string("filename"))
				new_filename=int(int(time.time())-(int(self.loaded_settings['file_duration'])/1000000000))
				#timestamp gives local time, we have to calculate difference between UTC and local
				timestamp_epoch = self.timestamp_at_midnight(new_filename)
				#crear una carpeta para guardar el fichero y otra para los thumbs
				subprocess.Popen("mkdir -p "+self.loaded_settings['file_path']+timestamp_epoch+"/thumbs", shell=True, stdout=subprocess.PIPE)
				new_filename=str(new_filename)
				long_path = self.loaded_settings['file_path']+'/'+timestamp_epoch+'/'
				new_filename = long_path+new_filename+".mp4"
				#subprocess.Popen("mv "+filename+" "+new_filename, shell=True, stdout=subprocess.PIPE)
				#Reparar fichero y moverlo ¿ -bsf:a aac_adtstoasc ? y #Crear un thumbnail cada hora y guardarlo en almacenamiento
				subprocess.Popen("ffmpeg -probesize 100M -analyzeduration 100M -i "+filename+" -c copy -movflags +faststart -bsf:a aac_adtstoasc "+new_filename+"; ffmpeg -probesize 100M -analyzeduration 100M -i "+new_filename+" -vf fps=1/3600 "+long_path+"thumbs/thumb%03d.jpg", shell=True, stdout=subprocess.PIPE)
				
				print("MIXTER LOG: Intentando crear fichero y thumbs: " + new_filename)
				self.log_message("[DEBUG] Intentando crear fichero y thumbs: " + new_filename)

	def on_sync_message(self, bus, message):
		t = message.type
		if t == Gst.MessageType.BUFFERING:
			percent = message.parse_buffering()
			if percent > 66:
				print("MIXTER LOG sync: Porcentaje de buffering (imprimir solo mas de 66%): " +str(percent))
				self.log_message("[BUFFER] (sync) Porcentaje: "+ str(percent))

	def on_stream_message(self, bus, message):
		type, owner = message.parse_stream_status()
		r = "STREAM: %s" % type, owner
		#print("MIXTER LOG message: Stream status" + str(r))
		#TODO definir niveles de log
		#self.log_message("[STREAMING]  " + str(r))

	#Manejar mensajes, sobre todo de error. Actuar de diferente manera segun sea el error, desactivando componentes o lo que convenga en cada caso
	def handle_msg(self, msg):
		if msg.find("Could not connect to RTMP stream") != -1:
			self.total_errors+=1
			print('MIXTER LOG: No se puede conectar por RTMP. Comprobar configuracion ' + str(self.total_errors))
			self.log_message("[ERROR] : No se puede conectar por RTMP. Comprobar configuracion")
			#time.sleep(4)
			if self.total_errors>=5:
				print('MIXTER LOG: demasiados intentos, se desactiva RMTP')
				self.log_message("[ERROR] : demasiados intentos, se desactiva RMTP")
				self.send_email('[ERROR] : demasiados intentos, se desactiva RMTP')
				self.loaded_settings['rtmp']='Off'
				#TODO lanzar un script que compruebe el estado del RTMP



#################################	
# Methods						#
#								#
#################################
	#TODO not the best way to do it and should return PLAYING, NULL, PAUSED...
	def check_pipeline_status(self):
		if self.gst_pipeline_state == 'PLAYING':
			return True
		else:
			return False

	""" 
	def kill_ffmpeg(self):
		#FIXME detectar mejor solo el proceso que queremos matar de FFMPEG
		subprocess.call("killall ffmpeg", shell=True)
		if self.ffmpeg_pid!=0:
			print("MIXTER LOG: Trying to kill FFMPEG..."+str(self.ffmpeg_pid))
			self.log_message('[DEBUG]  Trying to kill  FFMPEG ...'+str(self.ffmpeg_pid))
			#subprocess.call("kill -9 "+str(self.ffmpeg_pid), shell=True)
			self.ffmpeg_pid = 0
		else:
			print("MIXTER LOG: FFMPEG no se esta ejecutando")
			self.log_message('[DEBUG]  FFMPEG no se esta ejecutando')
	"""

	def log_message(self, message):
		file_log = open(self.loaded_settings['log_path']+'/mixter.log','a')
		file_log.write('['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']' + message + '\n') 
		file_log.close()
		#Acortar mensaje
		#message = message[0:80]
		if len(self.log_window_message.split('\n'))>10:
			logs_splited=self.log_window_message.split('\n',1)[1]
			self.log_window_message=str(logs_splited)
		self.log_window_message += '['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']' + message + '\n'
		try:
			self.log_window.set_text(self.log_window_message)
		except:
			pass


	def disconnect(self, n, m=0):
		Gtk.main_quit()

	#El check solo tiene que devolver el valor, otra funcion se encargara de actuar en consecuencia
	def check_shm(self):
		mem_available = subprocess.Popen("df -k /dev/shm/ | awk 'NR==2 {print $4}'", shell=True, stdout=subprocess.PIPE)
		mem_available = int(mem_available.stdout.read())
		return mem_available
	
	def check_ram(self):
		mem_available = subprocess.Popen("free | awk 'NR==2 {print $3}'", shell=True, stdout=subprocess.PIPE)
		mem_available = int(mem_available.stdout.read())
		return mem_available
	#FIXME MAL HECHO, esto da falsos positivos probablemente hay que pasar el resultado a FLOAT
	def check_cpu(self):
		cpu_usage =  subprocess.Popen("uptime | grep -ohe 'load average[s:][: ].*' | awk '{ print $3}' | sed -s 's/,$//gi'", shell=True, stdout=subprocess.PIPE)
		#para sacar solo entero:" uptime | grep -ohe 'load average[s:][: ].*' | awk '{ print substr ($3, 0, 1)}'"
		cpu_usage = cpu_usage.stdout.read().decode("utf-8").rstrip()
		cores_number = subprocess.Popen("nproc", shell=True, stdout=subprocess.PIPE)
		cores_number = cores_number.stdout.read().decode("utf-8").rstrip()
		if cpu_usage[0:1]>=cores_number:
			print("MIXTER LOG: Uso de CPU elevado, Intentando relanzar Obplayer y Snowmix")
			self.log_message("[WARNING] Uso de CPU elevado, Intentando matar y relanzar Obplayer y Snowmix")
			#self.send_email("[WARNING] Uso de CPU elevado, Intentando matar y relanzar Obplayer y Snowmix")
			print("MIXTER LOG: Desactivado el reinicio por uso de CPU elevado")
			self.log_message("[WARNING] Desactivado el reinicio por uso de CPU elevado")
			#self.restart_all(1)
		return cpu_usage+'/'+cores_number
		

	def check_shm_and_restart(self):
		mem_available = self.check_shm()
		if mem_available < 1000000:
			print("MIXTER LOG: WARNING, Memoria compartida a punto de rebasar, disponible solo: " + str(mem_available))
			self.log_message("[WARNING] Memoria compartida a punto de rebasar, disponible solo: " + str(mem_available))			
			#Si el mem_available es menor que X borrar /dev/shm y relanzar todo
			self.restart_all(1)	
			#print("MIXTER LOG: DESACTIVADO EL REINICIO POR FALTA DE SHM")
		else:
			print("MIXTER LOG: Memoria compartida disponible: " + str(mem_available))

	#dado el nombre de un proceso, verificar si existe
	def check_process(self,process):
		if process == 'brave':
			try:
				request = requests.get(self.loaded_settings['brave_path']+'/api/outputs', data='',timeout=1);
				if request.status_code == 200:
					return True
				else:
					return False
			except:
				return False

		process_check = subprocess.call('ps -U `whoami` | grep "'+process+'"', shell=True)
		if process_check==1:
			return False
		else:
			# meter el proceso en el array de procesos y hacerlo solo con los del usuario
			process_pid =  subprocess.Popen("ps -U `whoami` | grep "+process+" |  awk 'NR==1{ print $1}'", shell=True, stdout=subprocess.PIPE)
			process_pid = process_pid.stdout.read().decode("utf-8").rstrip()	
			if not process_pid in self.processes:
				self.processes.extend([process_pid])
			return True

	def execute_program(self,program):
		self.log_message("[DEBUG] Ejecutando " + program)
		print('MIXTER LOG: Ejecutando ' + program)

		if self.check_process(program):
			self.log_message("[DEBUG] "+program+" deberia estar funcionando")
			print('MIXTER LOG: '+program+' deberia estar funcionando')
		else:
			if program == 'snowmix':
				try:
					#subprocess.call("/usr/local/lib/Snowmix-0.5.1/scripts/obplayer", shell=True)
					file_log = open(self.loaded_settings['log_path']+'/snowmix.log','a')
					p = subprocess.Popen("/bin/bash /usr/local/lib/Snowmix-0.5.1/scripts/obplayer", shell=True,  stdout=file_log)
					file_log.close()
					#we need to wait for the snowmix/obplayer script to finish
					time.sleep(5)
				except:
					self.log_message("[ERROR] snowmix no pudo ejecutarse")
					print('MIXTER LOG: snowmix no pudo ejecutarse')

			elif program == 'obplayer':
				try:
					subprocess.Popen(self.loaded_settings['obplayer_path'], shell=True, stdout=subprocess.PIPE)
					#subprocess.Popen(args=['gnome-terminal', '--' ,self.loaded_settings['obplayer_path']])	
				except:
					#subprocess.Popen(args=['xterm', '-e' , self.loaded_settings['obplayer_path']])
					#subprocess.Popen(self.loaded_settings['obplayer_path'])
					print('MIXTER LOG: unable to launch '+program)

			elif program == 'brave':
				try:
					self.restart_brave()
				except:
					self.log_message("[ERROR] brave no pudo reiniciarse")
					print('MIXTER LOG: brave no pudo reiniciarse')

	def restart_brave(self):
		print('MIXTER LOG: Restarting brave...')
		self.log_message("[DEBUG] Restarting brave...")
		requests.post(self.loaded_settings['brave_path']+'/api/restart', data= '{"config":"current"}');

	def cleanup_tmp(self, widget):
		print('MIXTER LOG: Eliminando archivos temporales...')
		self.log_message("[DEBUG] Eliminando archivos temporales...")
		subprocess.call('rm -rf /tmp/audio* /tmp/video* /tmp/mixer* /tmp/mixter* /tmp/feed* /tmp/audioSn* /tmp/brave*', shell=True)

	def cleanup_shm(self, widget):
		print('MIXTER LOG: Eliminando archivos temporales y vaciando /dev/shm...')
		self.log_message("[DEBUG] Eliminando archivos temporales y vaciando /dev/shm...'")
		#DANGEROUS! be carefull with other users
		subprocess.call('rm -rf /dev/shm/shm*', shell=True)

	def flush(self, widget):
		now=datetime.datetime.now().strftime("%Y%m%d-%H_%M%p")
		print('MIXTER LOG: Renombrando mixterlog a mixterlog-'+now+' ...')
		self.log_message("[DEBUG] Flush log: Log cerrado "+now)
		subprocess.call('mv  '+self.loaded_settings['log_path']+'/mixter.log '+self.loaded_settings['log_path']+'/'+now+'.mixter.log', shell=True)
		print('MIXTER LOG: Renombrando mixterlog a mixterlog-'+now+' ...')
		self.log_message("[DEBUG] Flush log: Log anterior cerrado en "+now+" .mixter.log")

	def kill_process(self,pid):
		print('MIXTER LOG: Trying to kill process ' + pid)
		self.log_message("[WARNING] Trying to kill process " + pid)
		self.processes.remove(pid)
		subprocess.call("kill -9 "+pid, shell=True)

	##TODO killall and restart, new way
	def clean_kill_and_restart(self):
		print('MIXTER LOG: Trying to clean and restart everything')
		self.log_message("[WARNING] *******Trying to clean and restart everything*******")
		self.kill_all_pipelines()
		self.cleanup_tmp(1)
		self.cleanup_shm(1)
		for process in self.processes:
			self.kill_process(process)

		if self.loaded_settings['snowmix'] == 'On':
			subprocess.call("killall  obplayer2feed output2shmsink output2shmsink_seba wish", shell=True)

		if self.loaded_settings['brave'] == 'On':
                    self.restart_brave()
                    self.launch_pipeline()

#################################	
# Notification channels			#
#			       				#
#################################

	def send_email(self, message):
		try:
			subprocess.call('python3 '+self.mixter_path+'/sendemail.py '+ message, shell=True)
			print('MIXTER LOG: email enviado')
			self.log_message("[DEBUG] email enviado")
		except:
			print('MIXTER LOG: No se pudo enviar email de alerta, comprobar el archivo de settings')
			self.log_message("[ERROR] No se pudo enviar email de alerta, comprobar el archivo de settings")

	def send_telegram_msg(self, message):
		try:
			requests.post(self.loaded_settings['telegram_notifications'], data='{"user":"admin","pass":"admin","msg":"'+message+'"}');  
			print('MIXTER LOG: mensaje Telegram enviado')
			self.log_message("[DEBUG] mensaje Telegram enviado")
		except:
			print('MIXTER LOG: No se pudo enviar mensaje Telegram de alerta, comprobar el archivo de settings')
			self.log_message("[ERROR] No se pudo enviar mensaje Telegram de alerta, comprobar el archivo de settings")
		
#################################	
# Helpers						#
#			       				#
#################################
	#Return epoch at 00:00 of the local date
	def timestamp_at_midnight(self, time_to_convert=time.time()):
		time_to_convert = int(time_to_convert)

		timestamp_UTC = int(datetime.datetime.utcfromtimestamp(time_to_convert).timestamp())
		timestamp_LOCAL = int(datetime.datetime.fromtimestamp(time_to_convert).timestamp())
		time_difference = timestamp_LOCAL - timestamp_UTC

		timestamp_epoch = int(int(timestamp_LOCAL) + int(time_difference))

		year_UTC = int(datetime.datetime.utcfromtimestamp(timestamp_epoch).strftime('%Y'))
		month_UTC = int(datetime.datetime.utcfromtimestamp(timestamp_epoch).strftime('%m'))
		day_UTC = int(datetime.datetime.utcfromtimestamp(timestamp_epoch).strftime('%d'))

		timestamp_at_midnight_UTC = int(int(datetime.datetime(year_UTC,month_UTC,day_UTC,(0)).timestamp() + int(time_difference)) )

		return str(timestamp_at_midnight_UTC)


	def settings_string_to_array(self,settings_list):
		settings_used = {}
		for n in settings_list:
			settings_used[n]=self.loaded_settings[n]
		return settings_used

#################################	
# Pipeline handlers				#
#			        			#
#################################
	def get_pipelines(self):
		return self.pipelines_desc

	def kill_pipeline(self,pipeline_number):
		print('MIXTER LOG: trying to kill pipeline ' + str(pipeline_number))
		pipeline_name = self.pipelines_desc[pipeline_number]['pipeline_settings']['pipeline_name']
		print(pipeline_name)
		if pipeline_name=='CONTINUITY':
			#self.pill2kill.set()
			self.CONTINUITY.suicide()
			del self.pipelines_desc[pipeline_number]
			self.log_message("[WARNING] Gstreamer Pipeline: trying to kill pipeline " + str(pipeline_number))

		#for ffmpeg pipelines, we need to kill the process and next one too? FIXME
		elif 'pipeline_type' in self.pipelines_desc[pipeline_number]['pipeline_settings'] and self.pipelines_desc[pipeline_number]['pipeline_settings']['pipeline_type']=='ffmpeg':
			self.log_message("[WARNING] FFmpeg Pipeline: trying to kill pipeline " + str(pipeline_number))
			subprocess.call("kill -9 "+str(self.pipelines_desc[pipeline_number]['pid']), shell=True)
			subprocess.call("kill -9 "+str(self.pipelines_desc[pipeline_number]['pid']+1), shell=True)
			del self.pipelines_desc[pipeline_number]
			
		else:
			self.pipelines[pipeline_number].set_state(Gst.State.NULL)
			self.gst_pipeline_state = 'NULL'
			self.pipelines[pipeline_number]=None
			self.busses[pipeline_number]=None
			del self.pipelines_desc[pipeline_number]
			self.log_message("[WARNING] Gstreamer Pipeline: trying to kill pipeline " + str(pipeline_number))

		#delete gstreamer graph if any
		try:
			print('MIXTER LOG: trying to delete graph')
			self.log_message("[DEBUG] trying to delete graph")
			subprocess.call('rm '+self.loaded_settings['gst_graph_path']+'p_'+str(pipeline_number)+'*', shell=True)
		except:
			pass

	def kill_all_pipelines(self):
		print('MIXTER LOG: trying to kill all pipelines')
		self.log_message("[WARNING] Pipelines: trying to kill all pipelines")

		for n in list(self.pipelines_desc):
			self.kill_pipeline(n)


	def reconnect(self,pipeline_number=0):
		#self.log_message("[DEBUG] Reconnect " + str(self.pipelines[pipeline_number].get_name()))
		#self.kill_ffmpeg()
		time.sleep(.5)
		pipeline_text = self.pipelines_desc[pipeline_number]['pipeline_text']
		pipeline_settings = self.pipelines_desc[pipeline_number]['pipeline_settings']
		try:
			self.pipelines[pipeline_number].set_state(Gst.State.NULL)
			self.gst_pipeline_state = 'NULL'
			self.pipelines[pipeline_number]=None
			self.busses[pipeline_number]=None
			del self.pipelines_desc[pipeline_number]
		except:
			print('MIXTER LOG: Reconnect GST failure: is there any gstreamer pipeline?')
			self.log_message("[ERROR] Reconnect GST failure: is there any gstreamer pipeline?")
		
		try:
			self.pipelineRTMP.set_state(Gst.State.NULL)
			self.gst_pipeline_state = 'NULL'
			self.pipelineRTMP=None
		except:
			pass	

		self.busses[pipeline_number]=None
		print('MIXTER LOG: Reconnect: executing build_pipeline')
		self.log_message("[WARNING] Reconnect: executing build_pipeline")
		self.build_pipeline(pipeline_text,pipeline_settings)

#################################	
# New methods					#
#			        			#
#################################

	def dot_to_png(self,pipeline_id):
		try:
			print('MIXTER LOG: trying to convert .dot to .png')
			self.log_message("[DEBUG] trying to convert .dot to .png")
			subprocess.call('dot -Tpng -o '+self.loaded_settings['gst_graph_path']+pipeline_id+'.png '+self.loaded_settings['gst_graph_path']+pipeline_id+'.dot', shell=True)
		except:
			pass

	def be_loop(self):
		#self.disconnect_pipeline()
		#Mixter()
		Gtk.main()

GObject.threads_init()
Gst.init(None)
