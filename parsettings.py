#!/usr/bin/env python
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
import configparser
import os
class parsettings(object):

	def __init__(self,path=None):
		if path:
			self.settings_path = path+'/mixter_settings.cfg'
		else:
			self.settings_path = '/var/www/html/obplayer/mixter_settings_copialegal.cfg'

		self.config = configparser.RawConfigParser()
		self.settings = {
            'input_1_type' : 'videotestsrc',
            'input_2_type' : 'videotestsrc',
			'rtmp_url_sink' : 'rtmp://',
			'video_1_src' : '/tmp/video',
			'audio_1_src' : '/tmp/audio',
			'color_format_1_src' : 'BGRA',
			'video_2_src' : '/tmp/video',
			'audio_2_src' : '/tmp/audio',
			'color_format_2_src' : 'BGRA',
			'tcp_ip_sink' : '127.0.0.1',
			'tcp_port_sink' : 5005,
			'tcp_ip_1_src' : '127.0.0.1',
			'tcp_port_1_src' : 5010,
			'tcp_ip_2_src' : '127.0.0.1',
			'tcp_port_2_src' : 5010,
			'udp_port_sink' : 33333,
			'udp_ip_sink' : '127.0.0.1',
			'udp_port_1_src' : 33333,
			'udp_port_2_src' : 33333,
			'udp_ip_1_src' : '127.0.0.1',
			'udp_ip_2_src' : '127.0.0.1',
			'file_bitrate_sink' : 1024,
			'file_duration_sink' : 86400000000000,
			'file_path_sink' : '/tmp',
			'file_tmp_path_sink' : '/tmp/tmp_video_%1d.ts',
			'auto_launch' : 'Off',
            'output_type' : 'window',
			'obplayer' : 'Off',
			'snowmix' : 'Off',
			'brave' : 'Off',
            'brave_path' : 'http://192.168.53.39:5001',
			'log_path' : '/home/administrador/.openbroadcaster/logs',
			'obplayer_path' : '/var/www/html/obplayer/obplayer_loop',
            'ffmpeg_path' : '/home/administrador/obplayer/ffmpeg',
			'audio' : 'Off',
			'video' : 'Off',
			'obplayer_shm_video_file' : '/tmp/video',
			'obplayer_shm_audio_file' : '/tmp/audio',
			'multicast_iface' : 'eno1',
			'service_name' : 'Tenerife 2030 TV development',
			'email_from' : 'iprojects@iter.es',
			'email_to' : 'jporteiro.cedei@iter.es',
			'email_user' : 'iprojects',
			'email_pass' : '20AKl31',
			'email_server' : 'smtp.iter.es',
			'cs_hostname_main' : 'MMXIX06031006',
			'cs_hostname_backup' : 'NOHAY',
			'cs_ip_main' : '192.168.21.186',
			'cs_ip_backup' : '192.168.53.39',
			'cs_send_emergency' : 1,
			'cs_enabled' : 1,
			'cs_folder' : '/home/administrador/obplayer/mixter/status',
			'cs_files_other_path' : '/tmp',
			'cs_files_get_method' : 'copy',
			'cs_multicast_main' : '239.6.6.6',
			'cs_multicast_backup' : '239.7.7.7',
			'email_port' : '586',
			'overlay' : 'Off',
			'default_DOG' : '',
			'telegram_notifications' : 'localhost:3333/msg',
			'pipeline_name' : 'pipeline_name',
			'gst_graph_path' : '/home/administrador/.openbroadcaster/gst_png/',
			'pipeline_list' : '',
			'pipeline_text' : '',
			'pipeline_type' : '',
			'video_sink' : '/tmp/mixter_video',
			'audio_sink' : '/tmp/mixter_video',
			'color_format_sink' : 'BGRA',
			'file_1_src' : '',
			'file_2_src' : ''

		}
		if not os.path.lexists(self.settings_path):
			print("MIXTER LOG PARSETTINGS: INFO, guardando opciones por defecto")			
			self.saveDefault()

	def loadSettings(self):
		try:
			self.config = configparser.RawConfigParser()
			self.config.read(self.settings_path)

			for n in self.settings:
				self.settings[n] = self.config.get('Settings', n)
			
			print("MIXTER LOG PARSETTINGS: INFO, configuracion cargada")
			return self.settings
		except:
			print("MIXTER LOG PARSETTINGS: ERROR, no se pudo cargar el archivo de configuracion o se cargo con errores")


	def saveSettings(self,settings):
		print(settings)
		try:
			self.loadSettings()
		except:
			print("MIXTER LOG PARSETTINGS: ERROR, no se pudo cargar el archivo de configuracion, se intenta guardar igualmente")

		try:
			self.config.remove_section('Settings')

		except configparser.NoSectionError:
			print('MIXTER LOG PARSETTINGS: Error al guardar las opciones')
		
		self.config.add_section('Settings')
		print(settings)
		for n in settings:
			if n in self.settings and settings[n] != self.settings[n]:
				self.settings[n]=settings[n]
		
		for m in self.settings:
			self.config.set('Settings', m, self.settings[m])

		with open(self.settings_path, 'w') as configfile:
			self.config.write(configfile)
		print("MIXTER LOG PARSETTINGS: INFO, se han guardado las opciones en " + self.settings_path)
		return self.settings
	
	def saveDefault(self):
		settings=self.settings.copy()
		return self.saveSettings(settings)
