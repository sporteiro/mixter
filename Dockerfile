FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
ENV DEBIAN_FRONTEND teletype
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
ENV TZ=Europe/Lisbon

RUN apt-get update && \
    apt-get install -yq \
	python3 \
	python3-pycurl \
	python3-openssl \
	python3-apsw \
	python3-magic \
	python3-dateutil \
	python3-requests \
	python3-gi \
	python3-gi-cairo \
	python3-gst-1.0 \
	gir1.2-gtk-3.0 \
	gir1.2-gdkpixbuf-2.0 \
	gir1.2-pango-1.0 \
	gir1.2-gstreamer-1.0 \ 
	gir1.2-gst-plugins-base-1.0 \
	gir1.2-gst-rtsp-server-1.0 \
	gir1.2-gst-plugins-bad-1.0 \
	gstreamer1.0-tools \
	gstreamer1.0-nice \
	gstreamer1.0-libav \ 
	gstreamer1.0-alsa \
	gstreamer1.0-pulseaudio \
	gstreamer1.0-plugins-base \ 
	gstreamer1.0-plugins-good \
	gstreamer1.0-plugins-bad \
	gstreamer1.0-plugins-ugly \
	libffi6 \
	libffi-dev \
	gobject-introspection \
	libcairo2-dev \
	libgirepository1.0-dev \
	pkg-config \ 
	python3-dev \
	python3-wheel \
	python3-pip \
	python3-websockets \
	python3-psutil \
	python3-uvloop \
	curl \
	git \
	psmisc 

RUN git clone --depth 1 https://github.com/sporteiro/mixter.git && \
    cd mixter

EXPOSE 8066
WORKDIR /mixter
CMD ["python3", "/mixter/http_server.py"]
