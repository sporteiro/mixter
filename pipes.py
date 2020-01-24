#!/usr/bin/env python
#Sebastian Porteiro 2017-20 seba@sebastianporteiro.com
class Pipes():

    def pipe_to_launch(self,settings):

        if settings['input_type'] == 'shm_src':
          
            if settings['output_type'] == 'rtmp': #TEE
                
                self.pipetext = "shmsrc socket-path="+settings['video_src']+"  is-live=true do-timestamp=1 ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! tee name=t  ! queue2 ! videoconvert ! video/x-raw,format=I420,width=1280,height=720,framerate=25/1 !  x264enc speed-preset=ultrafast tune=zerolatency key-int-max=12 ! video/x-h264 ! h264parse ! video/x-h264 ! queue2 ! flvmux name=mux streamable=true  shmsrc socket-path="+settings['audio_src']+" do-timestamp=1 is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audioconvert  ! audioresample ! audio/x-raw,rate=44100 ! voaacenc bitrate=192000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux. mux. ! rtmpsink sync=false location="+settings['rtmp_url']+" t. ! queue2 ! videoconvert ! autovideosink "

            elif settings['output_type'] == 'udp': 

                if settings['overlay'] == 'Off':
                    self.pipetext = "shmsrc socket-path="+settings['video_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! videoconvert ! x264enc tune=zerolatency speed-preset=veryfast ! mpegtsmux name=mux ! rtpmp2tpay ! queue ! udpsink sync=false host="+settings['udp_ip']+" port="+settings['udp_port']+" shmsrc socket-path="+settings['audio_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audioconvert ! audioconvert  ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=192000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."
                else:
                    self.pipetext = "shmsrc socket-path="+settings['video_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3 ! videoconvert ! x264enc tune=zerolatency speed-preset=veryfast ! mpegtsmux name=mux ! rtpmp2tpay ! queue ! udpsink sync=false host="+settings['udp_ip']+" port="+settings['udp_port']+" shmsrc socket-path="+settings['audio_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audioconvert ! audioconvert  ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=192000 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."

            elif settings['output_type'] == 'tcp':

                if settings['overlay'] == 'Off':
                    self.pipetext = "shmsrc socket-path="+settings['audio_src']+" do-timestamp=true is-live=true ! queue ! audio/x-raw,format=S16LE, layout=interleaved, rate=48000, channels=2 ! audioconvert ! avenc_aac bitrate=192000 compliance=-2 ! audio/mpeg,mpegversion=4, stream-format=raw ! aacparse ! queue ! muxer. shmsrc socket-path="+settings['video_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! queue ! videoconvert ! x264enc tune=zerolatency speed-preset=3 key-int-max=50 bframes=0 ! video/x-h264, alignment=au, stream-format=byte-stream, profile=main ! h264parse ! queue ! flvmux name=muxer streamable=true ! queue ! tcpserversink host="+settings['tcp_ip']+" port="+settings['tcp_port']+" sync-method=2 recover-policy=keyframe"
                else:
                    self.pipetext = "shmsrc socket-path="+settings['audio_src']+" do-timestamp=true is-live=true ! queue ! audio/x-raw,format=S16LE, layout=interleaved, rate=48000, channels=2 ! audioconvert ! avenc_aac bitrate=192000 compliance=-2 ! audio/mpeg,mpegversion=4, stream-format=raw ! aacparse ! queue ! muxer. shmsrc socket-path="+settings['video_src']+"  is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! gdkpixbufoverlay name=svgoverlay1 location="+settings['default_DOG']+" ! gdkpixbufoverlay name=svgoverlay2 ! cairooverlay name=textoverlay ! gdkpixbufoverlay name=svgoverlay3 !  videoconvert ! video/x-raw,format=RGBA,width=1280,height=720,framerate=25/1 ! videoconvert ! x264enc tune=zerolatency speed-preset=3 key-int-max=50 bframes=0 ! video/x-h264, alignment=au, stream-format=byte-stream, profile=main ! h264parse ! queue ! flvmux name=muxer streamable=true ! queue ! tcpserversink host="+settings['tcp_ip']+" port="+settings['tcp_port']+" sync-method=2 recover-policy=keyframe"

            elif settings['output_type'] == 'file':
            
                self.pipetext = "shmsrc socket-path="+settings['video_src']+" is-live=true do-timestamp=true   ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! tee name=t  ! queue ! videomixer ! videoconvert ! x264enc tune=zerolatency speed-preset=ultrafast  ! h264parse ! mpegtsmux name=mux ! multifilesink post-messages=true location="+settings['file_tmp_path']+" max-files=3 next-file=5 max-file-duration="+settings['file_duration']+"  sync=false  t. ! queue ! videoconvert ! autovideosink shmsrc socket-path="+settings['audio_src']+" do-timestamp=true is-live=true ! audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2 ! audiomixer ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=128 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."
			
            else:

                 self.pipetext = "shmsrc socket-path="+settings['video_src']+" is-live=true typefind=true do-timestamp=true ! video/x-raw,format="+settings['video_format']+",width=1280,height=720,framerate=25/1 ! videoconvert ! autovideosink shmsrc socket-path="+settings['audio_src']+" ! "'audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2'" ! audioconvert ! autoaudiosink"


        elif settings['input_type'] == 'udp_src':
        
            if settings['output_type'] == 'file':
                self.pipetext = "udpsrc multicast-group="+settings['udp_ip_src']+" port="+settings['udp_port_src']+" ! decodebin ! videoconvert ! queue ! x264enc tune=zerolatency speed-preset=ultrafast bitrate="+settings['file_bitrate'] +" ! h264parse ! mpegtsmux name=mux ! multifilesink post-messages=true location="+settings['file_tmp_path']+" max-files=3 next-file=5 max-file-duration="+settings['file_duration']+" udpsrc udpsrc multicast-group="+settings['udp_ip_src']+" port="+settings['udp_port_src']+" ! typefind ! tsdemux ! queue !  mpegaudioparse ! avdec_mp2float ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=128 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."

            else:
                self.pipetext = "playbin uri=udp://"+settings['udp_ip_src']+":"+settings['udp_port_src']


        elif settings['input_type'] == 'rtp_src':

            if settings['output_type'] == 'file':
                self.pipetext = "udpsrc multicast-group="+settings['udp_ip_src']+" port="+settings['udp_port_src']+" caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=MP2T, payload=96\" ! rtpmp2tdepay ! decodebin ! videoconvert ! video/x-raw,format=I420,width=720,height=576,framerate=25/1 ! videoconvert ! queue2 ! videoconvert ! queue ! x264enc tune=zerolatency speed-preset=ultrafast bitrate="+settings['file_bitrate']+" ! h264parse ! mpegtsmux name=mux ! multifilesink post-messages=true location="+settings['file_tmp_path']+" max-files=3 next-file=5 max-file-duration="+settings['file_duration']+" udpsrc multicast-group="+settings['udp_ip_src']+" port="+settings['udp_port_src']+" ! typefind ! tsdemux ! queue !  mpegaudioparse ! avdec_mp2float ! audioconvert ! audioresample ! audio/x-raw,rate=48000 ! voaacenc bitrate=128 ! audio/mpeg ! aacparse ! audio/mpeg, mpegversion=4 ! queue2 ! mux."

            else:
                self.pipetext = "playbin uri=udp://"+settings['udp_ip_src']+":"+settings['udp_port_src']

        elif settings['input_type'] == 'udp_mp4_src':

            self.pipetext = "udpsrc multicast-group="+settings['udp_ip_src']+" port="+settings['udp_port_src']+" caps=\"application/x-rtp, media=video, clock-rate=90000\" ! rtpmp2tdepay ! decodebin ! videoconvert ! video/x-raw,format=BGRA,width=1280,height=720,framerate=25/1 ! videoconvert ! queue2 ! videoconvert ! queue ! autovideosink udpsrc multicast-group="+settings['udp_ip_src']+" port="+settings['udp_port_src']+" caps=\"application/x-rtp\" ! rtpmp2tdepay ! decodebin ! queue ! autoaudiosink"

        elif settings['input_type'] == 'tcp_src':

            #self.pipetext = "videotestsrc pattern=smpte ! video/x-raw,width=320,height=240 ! fakesink"
            self.pipetext = '0'
       
        else:
            self.pipetext = "videotestsrc pattern=snow ! video/x-raw,width=1280,height=720 ! autovideosink"
        #debug
        print('GST PIPE: ' + self.pipetext)
        return self.pipetext


