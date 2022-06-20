#!/usr/bin/env python3
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
import sys
import gi
gi.require_version('Gst', '1.0')
gi.require_version('GLib', '2.0')
gi.require_version('GObject', '2.0')
from gi.repository import GLib, GObject, Gst
import subprocess
import os
import time
import datetime

ID=1

class ProbeData:
    def __init__(self, pipe, src, audio_src):
        self.pipe = pipe
        self.src = src
        self.audio_src = audio_src
        #Gst.debug_bin_to_dot_file(pipe,Gst.DebugGraphDetails(15),'A_first_src')

class Continuity():
    def main(self,settings):
        self.settings=settings
        print('[continuity.py] ' + str(datetime.datetime.now()) + ' - Settings ' + str(settings))
        global ID
        try:
	        subprocess.call('rm -rf '+self.settings['video_sink']+' '+ self.settings['audio_sink'], shell=False)
        except:
            pass
        GObject.threads_init()
        Gst.init(None)

        #we create the dynamic pipeline
        pipe = Gst.Pipeline.new('dynamic')

        #VIDEO ELEMENTS
        #elements for the background branch
        src_bkg = Gst.ElementFactory.make('videotestsrc','videotestsrc1')
        src_bkg.set_property('pattern', 2)
        #src.set_property('num-buffers', 500)

        caps1 = Gst.ElementFactory.make('capsfilter', "videocapsfilter1")
        caps1.set_property('caps', Gst.Caps.from_string("video/x-raw,format="+self.settings['color_format_sink']+",width=1,height=1,framerate=25/1"))
        videoconvert1 = Gst.ElementFactory.make('videoconvert','videoconvert1')

        #elements for the visible branch
        src_top = Gst.ElementFactory.make('shmsrc','shmsrc_video_'+str(ID))
        src_top.set_property('socket-path', self.settings['video_1_src'])
        src_top.set_property('is-live', True)
        src_top.set_property('do-timestamp', True)
        src_top.set_property('blocksize', 0)

        caps2 = Gst.ElementFactory.make('capsfilter', "videocapsfilter2")
        caps2.set_property('caps', Gst.Caps.from_string("video/x-raw,format="+self.settings['color_format_sink']+",width=1280,height=720,framerate=25/1"))
        videoconvert2 = Gst.ElementFactory.make('videoconvert','videoconvert2')
        videoconvert3 = Gst.ElementFactory.make('videoconvert','videoconvert3')
        queue1 = Gst.ElementFactory.make('queue','queue_'+str(ID))
        queue1.set_property('flush-on-eos',True)
        #queue1.set_property('leaky',False)

        #use this sink to watch the output on the screen
        #sink = Gst.ElementFactory.make('autovideosink','sink_1')

        #mixer can be videomixer or compositor
        videomixer1 = Gst.ElementFactory.make('compositor', "videomixer1")
        videomixer1.set_property('background', 1)
        #videomixer1 = Gst.ElementFactory.make('videomixer', "videomixer1")
        
        #we send the video to a shmsink
        sink = Gst.ElementFactory.make('shmsink','sink_1')
        sink.set_property('socket-path',self.settings['video_sink'])
        sink.set_property('wait-for-connection', False)
        sink.set_property('sync', True)

        #we add everything to the pipeline
        pipe.add(src_top,src_bkg,caps1,caps2,videoconvert1,videoconvert2,videoconvert3,videomixer1,queue1,sink)
        
        #linking each element

        src_bkg.link(caps1)
        caps1.link(videoconvert2)
        videoconvert2.link(videomixer1)


        src_top.link(caps2)
        caps2.link(videoconvert1)
        videoconvert1.link(queue1)
        queue1.link(videomixer1)


        videomixer1.link(videoconvert3)
        videoconvert3.link(sink)


        #AUDIO ELEMENTS

        #elements for the background branch
        src_audio_bkg = Gst.ElementFactory.make('audiotestsrc','audiotestsrc2')
        src_audio_bkg.set_property('wave',4)
        caps_audio2 = Gst.ElementFactory.make('capsfilter', "audiocapsfilter2")
        caps_audio2.set_property('caps', Gst.Caps.from_string("audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2"))
        audioconvert3 = Gst.ElementFactory.make('audioconvert','audioconvert3')

        #elements for the visible branch
        src_audio = Gst.ElementFactory.make('shmsrc','shmsrc_audio_'+str(ID))
        src_audio.set_property('socket-path', self.settings['audio_1_src'])
        src_audio.set_property('is-live', True)
        src_audio.set_property('do-timestamp', True)


        caps_audio = Gst.ElementFactory.make('capsfilter', "audiocapsfilter1")
        caps_audio.set_property('caps', Gst.Caps.from_string("audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2"))
        audioconvert1 = Gst.ElementFactory.make('audioconvert','audioconvert1')
        audioconvert2 = Gst.ElementFactory.make('audioconvert','audioconvert2')

        audiomixer1 = Gst.ElementFactory.make('audiomixer', "audiomixer1")

        queue2 = Gst.ElementFactory.make('queue','queue_audio_'+str(ID))
        queue2.set_property('flush-on-eos',True)
        #queue2.set_property('leaky','downstream')
        #queue2.set_property('flush-on-eos',True)
        #queue2.set_property('min-threshold-time',5000000000)
        #queue2.set_property('max-size-time',18446744073709551615)


        #we send the audio to a shmsink
        sink_audio = Gst.ElementFactory.make('shmsink','sink_2')
        sink_audio.set_property('socket-path',self.settings['audio_sink'])
        sink_audio.set_property('wait-for-connection', False)
        sink_audio.set_property('sync', True)

        #add elements to pipeline
        pipe.add(src_audio,caps_audio,queue2,audioconvert1,sink_audio,audiomixer1,audioconvert2,src_audio_bkg,caps_audio2,audioconvert3)

        #linking each element
        src_audio.link(caps_audio)
        caps_audio.link(audioconvert1)
        audioconvert1.link(queue2)
        queue2.link(audiomixer1)

        src_audio_bkg.link(caps_audio2)
        caps_audio2.link(audioconvert3)
        audioconvert3.link(audiomixer1)

        audiomixer1.link(audioconvert2)
        audioconvert2.link(sink_audio)

        pdata = ProbeData(pipe, src_top,src_audio)
        self.loop = GObject.MainLoop()
        
        #connect bus to get msgs
        bus = pipe.get_bus()
        bus.add_signal_watch()
        bus.connect ("message", self.bus_call, self.loop, pdata)

        # start play back and listen to events
        pipe.set_state(Gst.State.PLAYING)
        #videotestsrc = pipe.get_by_name('vts1')
        #videotestsrc.set_property('pattern',1)
        #Gst.debug_bin_to_dot_file(pipe,Gst.DebugGraphDetails(15),'B_shm_pipe')

        try:
          self.loop.run()
        except:
          pass
        
        # cleanup
        pipe.set_state(Gst.State.NULL)
        #subprocess.call('/home/sporteiro/Desarrollo/easymixer/dottopng.sh', shell=False)


    def bus_call(self,bus, message, loop,pdata):
        shm_id = pdata.src.get_name()
        #print('shm_id: ' + shm_id)
        t = message.type
        if t == Gst.MessageType.EOS:
            print('[continuity.py] ' + str(datetime.datetime.now()) + ' - EOS message ')
            #sys.stdout.write("End-of-stream\n")
            #self.loop.quit()
            #reconnect(pdata)

        elif t == Gst.MessageType.ERROR:
            print('[continuity.py] ' + str(datetime.datetime.now())+' - ERROR message bus_call, shm_id ' + shm_id)
            err, debug = message.parse_error()
            #sys.stderr.write("Error: %s: %s\n" % (err, debug))
            print('[continuity.py] ' + str(datetime.datetime.now())+' - ERROR %s: %s\n' % (err, debug))
            #if shmsrc_number1!=None:
            #    reconnect(pdata)
            error_from = str(debug.split(':')[-2])
            print('[continuity.py] ' + str(datetime.datetime.now()) + ' - ERROR from: '+str(error_from))
            
            if error_from==shm_id:
                self.reconnect(pdata,shm_id)

        return True


    def reconnect_function(self,pdata,shm_id=0):#this works sometimes...
        global ID

        #print('[continuity.py]' + str(datetime.datetime.now()) + ' - reconnect element: '+str(shm_id)+', reconect_function ID: ' +str(ID))
        
        if os.path.lexists(self.settings['video_1_src']):
            print('[continuity.py] ' + str(datetime.datetime.now()) + ' - reconnect element: '+str(shm_id)+', reconect_function ID: ' +str(ID))
            pipeline = pdata.pipe
            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'C_shm_pipe_reconnect_'+str(ID))
        
            #first we identify elements and we set them to NULL before unlink and remove from pipeline

            #shm_src = pipeline.get_by_name('shmsrc_number1')
            shm_src = pipeline.get_by_name(str(shm_id))
            capsfilter = pipeline.get_by_name('videocapsfilter2')
            vc1 = pipeline.get_by_name('videoconvert1')
            sink_1 = pipeline.get_by_name('sink_1')
            videomixer1 = pipeline.get_by_name('videomixer1')
            queue1 = pipeline.get_by_name('queue1')

            
            capsfilter.set_state(Gst.State.NULL)
            vc1.set_state(Gst.State.NULL)
            shm_src.set_state(Gst.State.NULL)
            shm_src.unlink(capsfilter)
            pipeline.remove(shm_src)

            try:
                qpast = pipeline.get_by_name('queue_'+str(ID))
                qpast.set_state(Gst.State.NULL)
                #qpast.unlink(videomixer1)
                #pipeline.remove(qpast)
            except:
                pass

            #unlink

            capsfilter.unlink(vc1)
            vc1.unlink(videomixer1)


            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'D_shm_pipe_reconnect_unlink_'+str(ID))

            #remove

            pipeline.remove(capsfilter)
            pipeline.remove(vc1)

            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'E_shm_pipe_remove_'+str(ID))

            capsfilter.unlink(vc1)
            vc1.unlink(videomixer1)

            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'F_unlinked_'+str(ID))


            #pdata.src = Gst.ElementFactory.make('videotestsrc','vts5')
            #pdata.src.set_property('pattern', 'blue')

            #Create again

            pdata.src = Gst.ElementFactory.make('shmsrc','shmsrc_video_'+str(ID+1))
            pdata.src.set_property('socket-path', self.settings['video_1_src'])
            pdata.src.set_property('is-live', True)
            pdata.src.set_property('do-timestamp', True)
            pdata.src.set_property('blocksize', 4294967295)


            caps_new = Gst.ElementFactory.make('capsfilter','videocapsfilter2')
            vc_new = Gst.ElementFactory.make('videoconvert','videoconvert1')
            q_new = Gst.ElementFactory.make('queue','queue_'+str(ID+1))
            q_new.set_property('flush-on-eos',True)
            #q2.set_property('leaky',True)
            caps_new.set_property('caps', Gst.Caps.from_string("video/x-raw,format="+self.settings['color_format_sink']+",width=1280,height=720,framerate=25/1"))
            pdata.pipe.add(caps_new,vc_new,pdata.src,q_new)

            pdata.src.link(caps_new)
            caps_new.link(vc_new)
            vc_new.link(q_new)
            q_new.link(videomixer1)

            pdata.src.sync_state_with_parent()

            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'G_new_src_'+str(ID))
            
            pdata.src.set_state(Gst.State.PLAYING)
            caps_new.set_state(Gst.State.PLAYING)
            vc_new.set_state(Gst.State.PLAYING)
            videomixer1.set_state(Gst.State.PLAYING)
            q_new.set_state(Gst.State.PLAYING)

            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'H_new_src_'+str(ID))

            pdata.src.sync_state_with_parent()
            caps_new.sync_state_with_parent()
            vc_new.sync_state_with_parent()
            sink_1.sync_state_with_parent()

            #Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'I_new_src_'+str(ID))

            self.reconnect_audio(pdata,ID,shm_id)

            ID+=1
        else:
            print('[continuity.py] ' + str(datetime.datetime.now())+' - there is no '+ self.settings['video_1_src'])
            time.sleep(.1)
            self.reconnect_function(pdata,shm_id)


    def reconnect_audio(self,pdata,ID,shm_id):

        print('[continuity.py] ' + str(datetime.datetime.now())+' - reconnect_audio: shm_id: '+str(shm_id)+' ID: '+str(ID))

        if os.path.lexists(self.settings['audio_1_src']):

            pipeline = pdata.pipe
            
            src_audio = pipeline.get_by_name('shmsrc_audio_'+str(ID))
            queue_audio = pipeline.get_by_name('queue_audio_'+str(ID))
            audiocapsfilter1 = pipeline.get_by_name('audiocapsfilter1')
            audioconvert1 = pipeline.get_by_name('audioconvert1')

            audiomixer1 = pipeline.get_by_name('audiomixer1')
            sink_audio = pipeline.get_by_name('sink_2')

            #delete elements
            try:
                qpast = pipeline.get_by_name('queue_audio_'+str(ID))
                qpast.set_state(Gst.State.NULL)
                qpast.unlink(audiomixer1)
                pipeline.remove(qpast)
            except:
                pass

            audiocapsfilter1.set_state(Gst.State.NULL)
            audioconvert1.set_state(Gst.State.NULL)
            src_audio.set_state(Gst.State.NULL)
     

            src_audio.unlink(audiocapsfilter1)
            pipeline.remove(src_audio)

            audiocapsfilter1.unlink(audioconvert1)
            audioconvert1.unlink(queue_audio)

            pipeline.remove(audiocapsfilter1)
            pipeline.remove(audioconvert1)

            #re create
            pdata.audio_src = Gst.ElementFactory.make('shmsrc','shmsrc_audio_'+str(ID+1))
            pdata.audio_src.set_property('socket-path', self.settings['audio_1_src'])
            pdata.audio_src.set_property('is-live', True)
            pdata.audio_src.set_property('do-timestamp', True)

            caps_audio = Gst.ElementFactory.make('capsfilter', "audiocapsfilter1")
            caps_audio.set_property('caps', Gst.Caps.from_string("audio/x-raw,format=S16LE,rate=48000,layout=interleaved, channels=2"))
            audioconvert1 = Gst.ElementFactory.make('audioconvert','audioconvert1')

            queue2 = Gst.ElementFactory.make('queue','queue_audio_'+str(ID+1))
            queue2.set_property('flush-on-eos',True)

            pdata.pipe.add(pdata.audio_src,caps_audio,queue2,audioconvert1)

            #linking each element
            pdata.audio_src.link(caps_audio)
            caps_audio.link(audioconvert1)
            audioconvert1.link(queue2)
            queue2.link(audiomixer1)

            pdata.audio_src.set_state(Gst.State.PLAYING)
            caps_audio.set_state(Gst.State.PLAYING)
            audioconvert1.set_state(Gst.State.PLAYING)
            queue2.set_state(Gst.State.PLAYING)
            audiomixer1.set_state(Gst.State.PLAYING)

            pdata.audio_src.sync_state_with_parent()
            caps_audio.sync_state_with_parent()
            audioconvert1.sync_state_with_parent()
            queue2.sync_state_with_parent()
            audiomixer1.sync_state_with_parent()
            sink_audio.sync_state_with_parent()


            self.delayed_disconnect_queue(pdata,ID)

            Gst.debug_bin_to_dot_file(pipeline,Gst.DebugGraphDetails(15),'CONTINUITY_'+str(ID))

        else:
            print('[continuity.py] ' + str(datetime.datetime.now()) + ' - there is no '+self.settings['audio_1_src'])
            time.sleep(.1)
            self.reconnect_audio(pdata,ID,shm_id)


    def delayed_disconnect_queue(self,pdata,ID):

        pipeline = pdata.pipe
        videomixer1 = pipeline.get_by_name('videomixer1')
        queue1 = pipeline.get_by_name('queue_'+str(ID))

        sink_pad = videomixer1.get_static_pad('sink_'+str(ID))
        #src_pad = videomixer1.get_static_pad('src')
        #check = Gst.Pad.is_blocked(sink_pad)
        #print('sink_0 pad is blocked?  ' + str(check))
        #check = Gst.Pad.is_blocked(sink_pad)
        #print('sink_0 pad is blocked?  ' + str(check))

        sink_pad.stop_task()

        queue1.unlink(videomixer1)
        pipeline.remove(queue1)

        videomixer1.remove_pad(sink_pad)

    def reconnect(self,pdata,shm_id=0,n=0):
        print('[continuity.py] ' + str(datetime.datetime.now()) + ' - executing reconnect ')
        self.reconnect_function(pdata,shm_id)
        time.sleep(3)

    def suicide(self):
        print('[continuity.py] ' + str(datetime.datetime.now()) + ' - Trying to exit ')
        self.loop.quit()
        #sys.exit()
        #sys.exit(self.main(sys.argv,500))

CONTINUITY = Continuity()
#CONTINUITY.main()
"""
if __name__ == '__main__':
    sys.exit(main(sys.argv))
"""
