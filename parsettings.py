#!/usr/bin/env python
#Sebastian Porteiro 2017-20 seba@sebastianporteiro.com
import configparser
import os
class parsettings(object):

	def __init__(self,path=None):
		if path:
			self.settings_path = path+'/mixter_settings.cfg'
		else:
			self.settings_path = 'mixter_settings.cfg'

		self.config = configparser.RawConfigParser()
		self.settings = {
			'auto_launch' : 'Off',
            'input_type' : 'videotestsrc',
            'output_type' : 'window',
			'log_path' : '/home/logs',
			'rtmp_url' : 'rtmp://',
			'audio' : 'Off',
			'video' : 'Off',
			'video_src' : '/tmp/video',
			'audio_src' : '/tmp/audio',
			'video_format' : 'BGRA',
			'tcp_ip' : '127.0.0.1',
			'tcp_port' : 5005,
			'tcp_ip_src' : '127.0.0.1',
			'tcp_port_src' : 5010,
			'udp_port' : 5006,
			'udp_ip' : '127.0.0.1',
			'udp_port_src' : 5013,
			'udp_ip_src' : '127.0.0.1',
			'multicast_iface' : 'eth0',
			'file_bitrate' : 1024,
			'file_duration' : 86400000000000,
			'file_path' : '/tmp',
			'file_tmp_path' : '/tmp/tmp_video_%1d.ts',
       		'service_name' : 'No',
			'overlay' : 'Off',
			'default_DOG' : ''
		}
		if not os.path.lexists(self.settings_path):
			print("MIXTER LOG PARSETTINGS: INFO, saving default settings")			
			self.saveDefault()

	def loadSettings(self):
		try:
			self.config = configparser.RawConfigParser()
			self.config.read(self.settings_path)

			for n in self.settings:
				self.settings[n] = self.config.get('Settings', n)
			
			print("MIXTER LOG PARSETTINGS: INFO, settings loaded")
			return self.settings
		except:
			print("MIXTER LOG PARSETTINGS: ERROR, settings file not loaded or with errors")


	def saveSettings(self,settings):
		print(settings)
		try:
			self.loadSettings()
		except:
			print("MIXTER LOG PARSETTINGS: ERROR, unable to load settings file, trying to save anyway")

		try:
			self.config.remove_section('Settings')

		except configparser.NoSectionError:
			print('MIXTER LOG PARSETTINGS: Error saving settings')
		
		self.config.add_section('Settings')
		print(settings)
		for n in settings:
			if n in self.settings and settings[n] != self.settings[n]:
				self.settings[n]=settings[n]
		
		for m in self.settings:
			self.config.set('Settings', m, self.settings[m])

		with open(self.settings_path, 'w') as configfile:
			self.config.write(configfile)
		print("MIXTER LOG PARSETTINGS: INFO, settings has been saved in " + self.settings_path)
		return self.settings
	
	def saveDefault(self):
		settings=self.settings.copy()
		return self.saveSettings(settings)
