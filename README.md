# MIXTER ![Alt text](https://github.com/sporteiro/mixter/blob/master/img/bw.png)
Gstreamer player with web interface

## Dependencies

### Minimum

	python3 
	python3-pycurl 
	python3-openssl 
	python3-apsw 
	python3-magic 
	python3-dateutil 
	python3-requests 
	python3-gi 
	python3-gi-cairo 
	python3-gst-1.0 
	gir1.2-gtk-3.0 
	gir1.2-gdkpixbuf-2.0 
	gir1.2-pango-1.0 
	gir1.2-gstreamer-1.0 
	gir1.2-gst-plugins-base-1.0 
	gir1.2-gst-rtsp-server-1.0 
	gir1.2-gst-plugins-bad-1.0
	gstreamer1.0-tools
	gstreamer1.0-nice
	gstreamer1.0-libav 
	gstreamer1.0-alsa 
	gstreamer1.0-pulseaudio 
	gstreamer1.0-plugins-base 
	gstreamer1.0-plugins-good 
	gstreamer1.0-plugins-bad 
	gstreamer1.0-plugins-ugly


### Recommended

	ntp 
	build-essential 
	gcc
	git 
	libffi6 
	libffi-dev
	gobject-introspection
	libcairo2-dev
	libgirepository1.0-dev
	pkg-config 
	python3-dev
	python3-wheel
	python3-pip
	python3-websockets
	python3-psutil
	python3-uvloop
	curl
	psmisc
	ubuntu-restricted-addons 
	ubuntu-restricted-extras 

## Usage

### Docker
Create image with:

	docker build -t mixter:0.2 -f Dockerfile .


Run container sharing port (default :8066) and volumes if required (ie. for settings)

	docker run -ti -p 8066:8066 -v /home/mixter_settings.cfg:/mixter/mixter_settings.cfg mixter:0.2


With or without `Docker` app would be running

	python3 ./http_server.py

Access the web interface with:

* user: user
* password: user

"Run pipeline" as many times as pipelines you need or as long as your machine doesn't melt

## How it works

### http_server.py

Is listening to configured port (default :8066). Can be accesed through HTML interface or called via API

### mixter.py

It manages Gstreamer pipelines stored in `pipes.py`, launching, killing, receiving messages etc.

### parsettings.py

Loads and saves settings file `mixter_settings.cfg`

