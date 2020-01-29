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
#for post requests
import requests
#Classes in different files
from pipes import Pipes
from parsettings import parsettings
#overlays
import json
import cairo
gi.require_foreign('cairo')

class Mixter(object):
	def __init__(self):
		print("*******MIXTER: Launching*******")
		#mixter path, useful for saving log or settings
		self.mixter_path=os.path.dirname(os.path.realpath(__file__))
		self.log_window_message = ''
		hostname =  subprocess.Popen("hostname", shell=True, stdout=subprocess.PIPE)
		self.hostname = hostname.stdout.read().decode("utf-8").rstrip()
		#print(self.hostname)
		#array of processes so we can check them
		self.mixter_settings_path = self.mixter_path
		#Pipeline is None when we start
		self.pipeline = None
		self.gst_pipeline_state = 'NULL'
		#load settings
		self.load_settings()
		self.pipeline_number = 0
		self.pipelines = {}
		self.pipelines_desc = {}
		self.busses = {}
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
			self.log_message('[DEBUG] Settings loaded')
		except:
			print('MIXTER LOG: ERROR, settings file not loaded or with errors')
			self.log_message('[ERROR] settings file not loaded or with errors')


	def launch_pipeline(self):
		#After settings are loaded, if auto_launch is On, we build gstreamer pipeline
		if self.loaded_settings['auto_launch']=='On':
			self.log_message("[DEBUG] auto_launch active, trying to launch")
			self.build_pipeline()
		else:
			self.log_message("[DEBUG] auto_launch not active, please launch manually")

#################################	
# GSTREAMER build Pipeline	    #
#				                #
#################################
	def build_pipeline(self,pipeline_text='',src='',sink=''):
		pipes = Pipes()
		pipeline_number = self.pipeline_number
		self.pipelines_desc[pipeline_number] = {}

		if pipes.pipe_to_launch(self.loaded_settings) != '0':
			if pipeline_text=='':
				self.pipelines[pipeline_number] = Gst.parse_launch(pipes.pipe_to_launch(self.loaded_settings))
				self.pipelines_desc[pipeline_number]['pipeline_text'] = str(pipes.pipe_to_launch(self.loaded_settings))
			else:
				self.pipelines[pipeline_number] = Gst.parse_launch(pipeline_text)
				self.pipelines_desc[pipeline_number]['pipeline_text'] = str(pipeline_text)

			print("MIXTER LOG: Launching from: " + self.loaded_settings['input_type'] + " to: " + self.loaded_settings['output_type'])
			self.log_message('[DEBUG] Launching from: ' + self.loaded_settings['input_type'] + " to: " + self.loaded_settings['output_type'])

			#connect bus
			self.busses[pipeline_number] = self.pipelines[pipeline_number].get_bus()
			self.busses[pipeline_number].add_signal_watch()
			self.busses[pipeline_number].enable_sync_message_emission()
			self.busses[pipeline_number].connect("message", self.on_message, pipeline_number)
			self.busses[pipeline_number].connect("sync-message::element", self.on_sync_message)
			self.busses[pipeline_number].connect("sync-message::stream-status", self.on_stream_message)

			self.pipelines[pipeline_number].set_name('pipeline_'+str(self.pipeline_number))
			print('MIXTER LOG: Pipeline built, bus connected')
			self.log_message('[DEBUG] Pipeline: Pipeline built, bus connected ' + str(self.pipelines[pipeline_number].get_name()))	
			#latencia 
			self.latency = self.pipelines[pipeline_number].get_latency()
			print('MIXTER LOG: Latency ' + str(self.latency))

			self.pipelines[pipeline_number].set_state(Gst.State.PLAYING)
			#TODO this is not the best way to check pipeline state
			self.gst_pipeline_state = 'PLAYING'
			print('MIXTER LOG: GST state ' + self.gst_pipeline_state)
			self.log_message('[DEBUG] GST state ' + self.gst_pipeline_state)

			self.pipelines_desc[pipeline_number]['name'] = str(self.pipelines[pipeline_number].get_name())
			self.pipelines_desc[pipeline_number]['src'] = src or str(self.loaded_settings['input_type'])
			self.pipelines_desc[pipeline_number]['sink'] = sink or str(self.loaded_settings['output_type'])


		self.pipeline_number += 1

#################################	
# Overlay			            #
#				                #
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
# Methods			            #
#				                #
#################################
	#TODO not the best way to do it and should return PLAYING, NULL, PAUSED...
	def check_pipeline_status(self):
		if self.gst_pipeline_state == 'PLAYING':
			return True
		else:
			return False

	def get_pipelines(self):
		return self.pipelines_desc

	def reconnect(self,pipeline_number=0):
		self.log_message("[DEBUG] Reconnect " + str(self.pipelines[pipeline_number].get_name()))
		time.sleep(.5)
		pipeline_text = self.pipelines_desc[pipeline_number]['pipeline_text']
		src = self.pipelines_desc[pipeline_number]['src']
		sink = self.pipelines_desc[pipeline_number]['sink']
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
		self.build_pipeline(pipeline_text,src,sink)

	def kill_pipeline(self,pipeline_number):

		self.pipelines[pipeline_number].set_state(Gst.State.NULL)
		self.gst_pipeline_state = 'NULL'
		self.pipelines[pipeline_number]=None
		self.busses[pipeline_number]=None
		del self.pipelines_desc[pipeline_number]
		self.log_message("[WARNING] Gstreamer Pipeline: trying to kill pipeline " + str(pipeline_number))

#################################	
# Logging			            #
#				                #
#################################
	def log_message(self, message):
		file_log = open(self.loaded_settings['log_path']+'/mixter.log','a')
		file_log.write('['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']' + message + '\n') 
		file_log.close()
		#message = message[0:80]
		if len(self.log_window_message.split('\n'))>10:
			logs_splited=self.log_window_message.split('\n',1)[1]
			self.log_window_message=str(logs_splited)
		self.log_window_message += '['+ datetime.datetime.now().strftime("%A, %d. %B %Y %H:%M%p:%S%p")+']' + message + '\n'
		try:
			self.log_window.set_text(self.log_window_message)
		except:
			pass

	def flush(self, widget):
		now=datetime.datetime.now().strftime("%Y%m%d-%H_%M%p")
		print('MIXTER LOG: renaming mixterlog as mixterlog-'+now+' ...')
		self.log_message("[DEBUG] Flush log: Log closed "+now)
		subprocess.call('mv  '+self.loaded_settings['log_path']+'/mixter.log '+self.loaded_settings['log_path']+'/'+now+'.mixter.log', shell=True)
		print('MIXTER LOG: renaming mixterlog as mixterlog-'+now+' ...')
		self.log_message("[DEBUG] Flush log: Log Log closed as "+now+".mixter.log")


#################################	
# Gstreamer messages            #
#				                #
#################################

	def on_message(self, bus, message, pipeline_number):
		#print("MIXTER LOG message: GST message received")
		t = message.type
		if t == Gst.MessageType.EOS:
			self.log_message("[ERROR] EOS from pipeline_"+ str(pipeline_number)+' '+ str(error))	
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
				print("MIXTER LOG message: buffering percentage (print above 60%): " + str(percent))
				self.log_message("[BUFFER] percentage: "+ str(percent))	
		
		elif t == Gst.MessageType.ELEMENT:
			msg = message.get_structure()
			msgstr=str(msg.get_name())
			if msgstr=="GstMultiFileSink":	
				print("MIXTER LOG: New file created")
				self.log_message("[DEBUG] New file created")

	def on_sync_message(self, bus, message):
		t = message.type
		if t == Gst.MessageType.BUFFERING:
			percent = message.parse_buffering()
			if percent > 66:
				print("MIXTER LOG sync: buffering percentage (print above 66%): " +str(percent))
				self.log_message("[BUFFER] (sync) percentage: "+ str(percent))

	def on_stream_message(self, bus, message):
		type, owner = message.parse_stream_status()
		r = "STREAM: %s" % type, owner

	def handle_msg(self, msg):
		if msg.find("Could not connect to RTMP stream") != -1:
			self.total_errors+=1
			print('MIXTER LOG: unable to connect to RTMP ' + str(self.total_errors))
			self.log_message("[ERROR] : unable to connect to RTMP")
			#time.sleep(4)
			if self.total_errors>=5:
				print('MIXTER LOG: too many failure attempts, RTMP deactivated')
				self.loaded_settings['rtmp']='Off'

	def be_loop(self):
		Gtk.main()

GObject.threads_init()
Gst.init(None)
