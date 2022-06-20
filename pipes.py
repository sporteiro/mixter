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
class Pipes():

    def pipe_to_launch(self,settings):
        if settings['input_2_type'] == 'none_2_src':
            if settings['input_1_type'] == 'shm_1_src':
                if settings['output_type'] == 'rtmp_sink': #con TEE
                    
                    self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true do-timestamp=1 ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! tee name=t  ! queue2 ! videoconvert ! video/x-raw,format=I420,width=1280,height=720,framerate=25/1 !  x264enc speed-preset=ultrafast tune=zerolatency key-int-max=12 ! video/x-h264 ! h264parse ! video/x-h264 ! queue2 ! flvmux name=mux streamable=true  shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=1 is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audioconvert  ! audioresample ! audio/x-raw,rate=44100 ! voaacenc bitrate=192000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux. mux. ! rtmpsink sync=false location="+settings['rtmp_url_sink']+" t. ! queue2 ! videoconvert ! autovideosink "

                    self.settings_needed = ["video_1_src","color_format_1_src","audio_1_src","rtmp_url_sink"]

                elif settings['output_type'] == 'udp_sink': #con TEE

                    #self.pipetext = "shmsrc socket-path="+settings['video_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! videomixer ! videoconvert ! tee name=t  ! queue ! videoconvert ! x264enc tune=zerolatency speed-preset=veryfast ! mpegtsmux name=mux ! rtpmp2tpay ! queue ! udpsink sync=false host="+settings['udp_ip_sink']+" port="+settings['udp_port_sink']+" t. ! queue ! videoconvert ! autovideosink sync=false shmsrc socket-path="+settings['audio_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audiomixer ! audioconvert ! tee name=t2 ! queue ! audioconvert  ! audioresample ! audio/x-raw,rate=44100 ! voaacenc bitrate=96000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux. t2. ! queue ! audioconvert  !  autoaudiosink sync=false"
                    #sinTEE

                    if settings['overlay'] == 'Off':
                        self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! videoconvert ! x264enc tune=zerolatency speed-preset=veryfast ! mpegtsmux name=mux ! rtpmp2tpay ! queue ! udpsink sync=false host="+settings['udp_ip_sink']+" port="+settings['udp_port_sink']+" shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audioconvert ! audioconvert  ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=192000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."
                    else:
                        self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3 ! videoconvert ! x264enc tune=zerolatency speed-preset=veryfast ! mpegtsmux name=mux ! rtpmp2tpay ! queue ! udpsink sync=false host="+settings['udp_ip_sink']+" port="+settings['udp_port_sink']+" shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audioconvert ! audioconvert  ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=192000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."

                    self.settings_needed = ["video_1_src","color_format_1_src","udp_ip_sink","udp_port_sink","audio_1_src","default_DOG","overlay"]

                elif settings['output_type'] == 'tcp_sink':

                    if settings['overlay'] == 'Off':
                        self.pipetext = "shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! queue ! audio/x-raw,format=S16LE, layout=interleaved, rate=48000, channels=2 ! audioconvert ! avenc_aac bitrate=192000 compliance=-2 ! audio/mpeg,mpegversion=4, stream-format=raw ! aacparse ! queue ! muxer. shmsrc socket-path="+settings['video_1_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! queue ! videoconvert ! x264enc tune=zerolatency speed-preset=3 key-int-max=50 bframes=0 ! video/x-h264, alignment=au, stream-format=byte-stream, profile=main ! h264parse ! queue ! flvmux name=muxer streamable=true ! queue ! tcpserversink host="+settings['tcp_ip_sink']+" port="+settings['tcp_port_sink']+" sync-method=2 recover-policy=keyframe"
                    else:
                        self.pipetext = "shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! queue ! audio/x-raw,format=S16LE, layout=interleaved, rate=48000, channels=2 ! audioconvert ! avenc_aac bitrate=192000 compliance=-2 ! audio/mpeg,mpegversion=4, stream-format=raw ! aacparse ! queue ! muxer. shmsrc socket-path="+settings['video_1_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3 !  videoconvert ! video/x-raw,format=BGRA,width=1280,height=720,framerate=25/1 ! videoconvert ! x264enc tune=zerolatency speed-preset=3 key-int-max=50 bframes=0 ! video/x-h264, alignment=au, stream-format=byte-stream, profile=main ! h264parse ! queue ! flvmux name=muxer streamable=true ! queue ! tcpserversink host="+settings['tcp_ip_sink']+" port="+settings['tcp_port_sink']+" sync-method=2 recover-policy=keyframe"

                    self.settings_needed = ["video_1_src","color_format_1_src","audio_1_src","default_DOG","tcp_ip_sink","tcp_port_sink","overlay"]

                elif settings['output_type'] == 'mpeg2_sink':

                    self.pipetext ="shmsrc socket-path="+settings['video_1_src']+" is-live=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! queue2 ! videoconvert ! videoscale ! video/x-raw,format=I420, width=720,height=576 ! videoscale ! videoconvert ! queue2 ! avenc_mpeg2video interlaced=1 bitrate=4800000 pass=0 bitrate-tolerance=0 gop-size=12 compliance=1 rc-max-rate=4800000 rc-min-rate=4800000 max-key-interval=12 max-bframes=3 ! mpegvideoparse ! queue2 ! mux.sink_101 mpegtsmux name=mux ! tsparse set-timestamps=True ! queue ! rtpmp2tpay ! queue ! udpsink host="+settings['udp_ip_sink']+" port="+settings['udp_port_sink']+" auto-multicast=1 buffer-size=5800000 shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! queue2 ! audioconvert ! twolamemp2enc bitrate=192 mode=1 ! audio/mpeg ! mpegaudioparse ! queue2 ! mux.sink_102"

                    self.settings_needed = ["video_1_src","color_format_1_src","audio_1_src","default_DOG","udp_ip_sink","udp_port_sink"]

                elif settings['output_type'] == 'file_sink':
                
                    self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true do-timestamp=true   ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! tee name=t  ! queue ! videomixer ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast  ! h264parse ! mpegtsmux name=mux ! multifilesink post-messages=true location="+settings['file_tmp_path_sink']+" max-files=3 next-file=5 max-file-duration="+settings['file_duration_sink']+"  sync=false  t. ! queue ! videoconvert ! autovideosink shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audiomixer ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=128 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."
			    

                    self.settings_needed = ["video_1_src","color_format_1_src","audio_1_src","file_tmp_path_sink","file_duration_sink"]
			    
		    
			    #FIXME no longer needed
                elif settings['output_type'] == 'tcp_udp_ffmpeg':

                    if settings['overlay'] == 'Off':
                        self.pipetext = "shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! queue ! audio/x-raw,format=S16LE, layout=interleaved, rate=48000, channels=2 ! audioconvert ! avenc_aac bitrate=192000 compliance=-2 ! audio/mpeg,mpegversion=4, stream-format=raw ! aacparse ! queue ! muxer. shmsrc socket-path="+settings['video_1_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! queue ! videoconvert ! x264enc tune=zerolatency speed-preset=3 key-int-max=50 bframes=0 ! video/x-h264, alignment=au, stream-format=byte-stream, profile=main ! h264parse ! queue ! flvmux name=muxer streamable=true ! queue ! tcpserversink host="+settings['tcp_ip_sink']+" port="+settings['tcp_port_sink']+" sync-method=2 recover-policy=keyframe"
                    else:
                        self.pipetext = "shmsrc socket-path="+settings['audio_1_src']+" do-timestamp=true is-live=true ! queue ! audio/x-raw,format=S16LE, layout=interleaved, rate=48000, channels=2 ! audioconvert ! avenc_aac bitrate=192000 compliance=-2 ! audio/mpeg,mpegversion=4, stream-format=raw ! aacparse ! queue ! muxer. shmsrc socket-path="+settings['video_1_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3 !  videoconvert ! video/x-raw,format=RGBA,width=1280,height=720,framerate=25/1 ! videoconvert ! x264enc tune=zerolatency speed-preset=3 key-int-max=50 bframes=0 ! video/x-h264, alignment=au, stream-format=byte-stream, profile=main ! h264parse ! queue ! flvmux name=muxer streamable=true ! queue ! tcpserversink host="+settings['tcp_ip_sink']+" port="+settings['tcp_port_sink']+" sync-method=2 recover-policy=keyframe"

			    #FIXME we use continuity.py in this case?
                elif settings['output_type'] == 'shm_sink':
                    
                    if settings['overlay'] == 'Off':
                        self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! videoconvert ! queue ! shmsink socket-path=/tmp/mixter"
                    else:
                        self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3  ! videoconvert ! queue ! shmsink socket-path=/tmp/mixter"
                else:
                    if settings['overlay'] == 'Off':
                        self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! videoconvert ! autovideosink shmsrc socket-path="+settings['audio_1_src']+" ! "'audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2'" ! audioconvert ! autoaudiosink"
                    else:
                        self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3 ! videoconvert ! autovideosink shmsrc socket-path="+settings['audio_1_src']+" ! "'audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2'" ! audioconvert ! autoaudiosink"
                        
                    self.settings_needed = ["video_1_src","color_format_1_src","audio_1_src"]





            elif settings['input_1_type'] == 'udp_1_src':
            
                if settings['output_type'] == 'file_sink':
                    self.pipetext = "udpsrc multicast-group="+settings['udp_ip_1_src']+" port="+settings['udp_port_1_src']+" ! decodebin ! videoconvert ! queue ! x264enc tune=zerolatency speed-preset=ultrafast bitrate="+settings['file_bitrate_sink'] +" ! h264parse ! mpegtsmux name=mux ! multifilesink post-messages=true location="+settings['file_tmp_path_sink']+" max-files=3 next-file=5 max-file-duration="+settings['file_duration_sink']+" udpsrc udpsrc multicast-group="+settings['udp_ip_1_src']+" port="+settings['udp_port_1_src']+" ! typefind ! tsdemux ! queue !  mpegaudioparse ! avdec_mp2float ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=128 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."

                    self.settings_needed = ["file_tmp_path_sink","file_duration_sink","file_bitrate_sink","udp_ip_1_src","udp_port_1_src"]

			    #FIXME no longer needed
                elif settings['output_type'] == 'udp_ffmpeg':
                    self.pipetext = "videotestsrc pattern=smpte ! video/x-raw,width=100,height=100 ! fakesink"

                else:
                    self.pipetext = "playbin uri=udp://"+settings['udp_ip_1_src']+":"+settings['udp_port_1_src']
                    self.settings_needed = ["udp_ip_1_src","udp_port_1_src"]


            elif settings['input_1_type'] == 'rtp_1_src':

                if settings['output_type'] == 'file_sink':
                    self.pipetext = "udpsrc multicast-group="+settings['udp_ip_1_src']+" port="+settings['udp_port_1_src']+" caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=MP2T, payload=96\" ! rtpmp2tdepay ! decodebin ! videoconvert ! video/x-raw,format=I420,width=720,height=576,framerate=25/1 ! videoconvert ! queue2 ! videoconvert ! queue ! x264enc tune=zerolatency speed-preset=ultrafast bitrate="+settings['file_bitrate_sink']+" ! h264parse ! mpegtsmux name=mux ! multifilesink post-messages=true location="+settings['file_tmp_path_sink']+" max-files=3 next-file=5 max-file-duration="+settings['file_duration_sink']+" udpsrc multicast-group="+settings['udp_ip_1_src']+" port="+settings['udp_port_1_src']+" ! typefind ! tsdemux ! queue !  mpegaudioparse ! avdec_mp2float ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=128 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."

                    self.settings_needed = ["file_tmp_path_sink","file_duration_sink","file_bitrate_sink","udp_ip_1_src","udp_port_1_src"]

                else:
                    self.pipetext = "playbin uri=udp://"+settings['udp_ip_1_src']+":"+settings['udp_port_1_src']
                    self.settings_needed = ["udp_ip_1_src","udp_port_1_src"]

            elif settings['input_1_type'] == 'udp_mp4_src':

                self.pipetext = "udpsrc multicast-group="+settings['udp_ip_1_src']+" port="+settings['udp_port_1_src']+" caps=\"application/x-rtp, media=video, clock-rate=90000\" ! rtpmp2tdepay ! decodebin ! videoconvert ! video/x-raw,format=BGRA,width=1280,height=720,framerate=25/1 ! videoconvert ! queue2 ! videoconvert ! queue ! autovideosink udpsrc multicast-group="+settings['udp_ip_1_src']+" port="+settings['udp_port_1_src']+" caps=\"application/x-rtp\" ! rtpmp2tdepay ! decodebin ! queue ! autoaudiosink"

		    #FIXME no longer needed AND not working
            elif settings['input_1_type'] == 'tcp_1_src':
                #self.pipetext = "tcpclientsrc port="+settings['tcp_port_1_src']+" host="+settings['tcp_ip_1_src']+" ! tsdemux ! h264parse ! avdec_h264 ! autovideosink"
                self.pipetext = "videotestsrc pattern=snow ! video/x-raw,width=1280,height=720 ! autovideosink"
        

            elif settings['input_1_type'] == 'file_1_src':
                if settings['output_type'] == 'shm_sink':
                    self.pipetext = "filesrc location="+settings['file_1_src']+" ! decodebin ! videoconvert ! shmsink socket-path="+settings['video_sink']+" audiotestsrc ! shmsink socket-path="+settings['audio_sink']+""
                    self.settings_needed = ["file_1_src","video_sink", "audio_sink","color_format_sink"]

                else:
                    self.pipetext = "filesrc location="+settings['file_1_src']+" ! decodebin ! videoconvert ! autovideosink"
                    self.settings_needed = ["file_1_src"]

            elif settings['input_1_type'] == 'videotest_1_src':
                if settings['output_type'] == 'shm_sink':
                    self.pipetext = "videotestsrc pattern="+settings['pattern']+" !  video/x-raw,format=BGRA,width=1280,height=720,framerate=25/1 ! videoconvert ! shmsink socket-path="+settings['video_sink']+" audiotestsrc wave=12 ! shmsink socket-path="+settings['audio_sink']+""
                else:
                    self.pipetext = "videotestsrc pattern="+settings['pattern']+" ! video/x-raw,width=1280,height=720 ! autovideosink audiotestsrc ! audioconvert ! autoaudiosink"
                    self.settings_needed = ["pattern"]


            elif settings['input_1_type'] == 'ximage_1_src':
                if settings['output_type'] == 'file_sink':
                    self.pipetext = "ximagesrc startx="+settings['startx']+" starty="+settings['starty']+" endx="+settings['endx']+" endy="+settings['endy']+" ! video/x-raw,framerate=5/1 ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast  ! h264parse ! mpegtsmux ! filesink location="+settings['file_path_sink']+""
                    self.settings_needed = ["file_path_sink","startx","starty","endx","endy"]
                else:
                    self.pipetext = "ximagesrc startx="+settings['startx']+" starty="+settings['starty']+" endx="+settings['endx']+" endy="+settings['endy']+" ! video/x-raw,framerate=5/1 ! videoconvert ! autovideosink"
                    self.settings_needed = ["startx","starty","endx","endy"]


            elif settings['input_1_type'] == 'v4l2_1_src':
                if settings['output_type'] == 'file_sink':
                    self.pipetext = "v4l2src ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast  ! h264parse ! mpegtsmux ! filesink location="+settings['file_path_sink']+""
                    self.settings_needed = ["file_path_sink"]
                else:
                    self.pipetext = "v4l2src ! autovideosink"
                    self.settings_needed = ["startx"]

            else:
                self.pipetext = "videotestsrc pattern=snow ! video/x-raw,width=1280,height=720 ! autovideosink"
              
        elif settings['input_2_type'] == 'file_2_src':
            if settings['input_1_type'] == 'shm_1_src':
                self.pipetext = "shmsrc socket-path="+settings['video_1_src']+" is-live=true do-timestamp=true ! video/x-raw,format="+settings['color_format_1_src']+",width=1280,height=720,framerate=25/1  ! videoconvert ! queue2 use-buffering=True max-size-bytes=4294967295 ! mixer. filesrc location="+settings['file_path_2_src']+" !  decodebin ! alpha method=custom target-r=128 target-b=128 target-g=255 black-sensitivity=128 white-sensitivity=128 ! videoconvert ! mixer. videomixer name=mixer ! videoconvert ! autovideosink sync=false"


        #debug
        print('GST PIPE: ' + self.pipetext)
        return self.pipetext

    #return FFMPEG pipeline
    def ffmpeg_pipeline(self,settings):
        self.ffmpeg_pipe = None
        if settings['input_1_type'] == 'tcp_1_src':

            if settings['output_type'] == 'udp_sink':

                self.ffmpeg_pipe = "-i  tcp://"+settings['tcp_ip_1_src']+":"+settings['tcp_port_1_src']+" -vcodec mpeg2video -pix_fmt yuv420p -me_method epzs -threads 4 -r 25 -g 12 -bf 3 -s 720x576 -b:v 4000k -bt 4000k -flags +ilme+ildct -alternate_scan 0 -top 1 -acodec mp2 -ac 2 -ab 192k -ar 48000 -async 1 -y -minrate 4000k -maxrate 4000k -bufsize 3500k -muxrate 4500k -flush_packets 0  -f mpegts -mpegts_original_network_id 0x1122 -mpegts_transport_stream_id 0x3344 -mpegts_service_id 0x5566 -mpegts_service_type 0x1 -mpegts_pmt_start_pid 0x1500 -mpegts_start_pid 0x150 -metadata service_provider='ITER' -metadata service_name='"+settings['service_name']+"' 'udp://"+settings['udp_ip_sink']+":"+settings['udp_port_sink']+"?pkt_size=1316'"

        elif settings['input_1_type'] == 'udp_1_src':

            if settings['output_type'] == 'udp_sink':
                self.ffmpeg_pipe = "-i  udp://"+settings['udp_ip_1_src']+":"+settings['udp_port_1_src']+" -vcodec mpeg2video -pix_fmt yuv420p -me_method epzs -threads 4 -r 25 -g 12 -bf 3 -s 720x576 -b:v 4000k -bt 4000k -flags +ilme+ildct -alternate_scan 0 -top 1 -acodec mp2 -ac 2 -ab 192k -ar 48000 -async 1 -y -minrate 4000k -maxrate 4000k -bufsize 3500k -muxrate 4500k -flush_packets 0  -f mpegts -mpegts_original_network_id 0x1122 -mpegts_transport_stream_id 0x3344 -mpegts_service_id 0x5566 -mpegts_service_type 0x1 -mpegts_pmt_start_pid 0x1500 -mpegts_start_pid 0x150 -metadata service_provider='ITER' -metadata service_name='"+settings['service_name']+"' 'udp://"+settings['udp_ip_sink']+":"+settings['udp_port_sink']+"?pkt_size=1316'"
            else:
                self.ffmpeg_pipe = None
        else:
            self.ffmpeg_pipe = None

        return self.ffmpeg_pipe


    def get_settings_needed(self):
        #input_1_type, input_2_type and output_type are always needed
        in_and_out = ["input_1_type","input_2_type","output_type","pipeline_name","pipeline_type","service_name"] 
        self.settings_needed.extend(in_and_out) 
        return self.settings_needed

		
"""
#los 7 casos originales con/sin audio-video y overlay

		else:
		
			if self.audio=='On' and self.video=='On' and self.ribbon=='On': #7
				self.pipeline = Gst.parse_launch("shmsrc socket-path="+settings['video_src']+"  is-live=true do-timestamp=true  ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! "+svgoverlay+" ! videoconvert ! video/x-raw,format=I420,width=1280,height=720,framerate=25/1 ! videoconvert !  videomixer ! videoconvert ! queue2 use-buffering=True max-size-bytes=4294967295 ! autovideosink sync=false   shmsrc socket-path="+settings['audio_src']+" is-live=true do-timestamp=true   ! "'audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2'" ! audiomixer ! audioconvert  !  autoaudiosink sync=false")
				
				#self.pipeline = Gst.parse_launch("shmsrc socket-path=/tmp/video  is-live=true do-timestamp=true  ! "+caps+"  ! videoconvert ! "+svgoverlay+" ! videomixer  ! videoconvert ! xvimagesink sync=false   shmsrc socket-path=/tmp/audio  is-live=true do-timestamp=true   ! "'audio/x-raw,format=S16LE,rate=44100,layout=interleaved, channels=2'" ! audiomixer  ! audioconvert  !  autoaudiosink sync=false")

			elif self.audio=='Off' and self.video=='On' and self.ribbon=='On': #3
				self.pipeline = Gst.parse_launch("shmsrc socket-path="+settings['video_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1  ! videoconvert ! "+svgoverlay+"  ! videoconvert ! autovideosink")


			elif self.audio=='On' and self.video=='Off' and (self.ribbon=='On' or self.ribbon=='Off'): # 4 o 5
				self.pipeline = Gst.parse_launch("shmsrc socket-path="+settings['audio_src']+"   ! "'audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2'" ! audioconvert  !  autoaudiosink")


			elif self.audio=='On' and self.video=='On' and self.ribbon=='Off': #6
				self.pipeline = Gst.parse_launch("shmsrc socket-path="+settings['video_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1  ! videoconvert ! autovideosink shmsrc socket-path="+settings['audio_src']+"   ! "'audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2'" ! audioconvert  !  autoaudiosink")
		
			elif self.audio=='Off' and self.video=='On' and self.ribbon=='Off': #2
				self.pipeline = Gst.parse_launch("shmsrc socket-path="+settings['video_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1  ! videoconvert ! autovideosink")

			else: # 0 y 1
				self.pipeline = Gst.parse_launch("videotestsrc pattern=snow ! video/x-raw,width=1280,height=720 ! autovideosink")

"""
