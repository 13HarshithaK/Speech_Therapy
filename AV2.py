import cv2
import pyaudio
import wave
import threading
import time
import subprocess
import os
import keyboard

class VideoRecorder():  

    # Video class based on openCV 
    def __init__(self):

        self.open = True
        self.device_index = 0
        self.fps = 24               # fps should be the minimum constant rate at which the camera can
        self.fourcc = "XVID"       # capture images (with no decrease in speed over time; testing is required)
        self.frameSize = (640,480) # video formats and sizes also depend and vary according to the camera used
        self.video_filename = "temp_video.avi"
        self.video_cap = cv2.VideoCapture(self.device_index,cv2.CAP_DSHOW)
        self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
        self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
        self.frame_counts = 1
        self.start_time = time.time()


    # Video starts being recorded 
    def record(self):

        counter = 1
        timer_start = time.time()
        timer_current = 0


        while(self.open==True):
            ret, video_frame = self.video_cap.read()
            if (ret==True):

                    self.video_out.write(video_frame)
                    #print (str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current))
                    self.frame_counts += 1
                    counter += 1
                    timer_current = time.time() - timer_start
                    time.sleep(0.16)
                    gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
                    cv2.imshow('video_frame', gray)
                    cv2.waitKey(1)
            else:
                break

                # 0.16 delay -> 6 fps
                # 


    # Finishes the video recording therefore the thread too
    def stop(self):
        print("vc.stop")

        if self.open==True:

            self.open=False
            self.video_out.release()
            self.video_cap.release()
            cv2.destroyAllWindows()

        else: 
            pass

    # Launches the video recording function using a thread          
    def start(self):
        video_thread = threading.Thread(target=self.record)
        video_thread.start()





class AudioRecorder():


    # Audio class based on pyAudio and Wave
    def __init__(self):

        self.open = True
        self.rate = 44100
        self.frames_per_buffer = 1024
        self.channels = 2
        self.format = pyaudio.paInt16
        self.audio_filename = "temp_audio.wav"
        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer = self.frames_per_buffer)
        self.audio_frames = []


    # Audio starts being recorded
    def record(self):

        self.stream.start_stream()
        while(self.open == True):
            data = self.stream.read(self.frames_per_buffer) 
            self.audio_frames.append(data)
            if self.open==False:
                break


    # Finishes the audio recording therefore the thread too    
    def stop(self):

        if self.open==True:
            self.open = False
            self.stream.stop_stream()
            self.stream.close()
            self.audio.terminate()

            waveFile = wave.open(self.audio_filename, 'wb')
            waveFile.setnchannels(self.channels)
            waveFile.setsampwidth(self.audio.get_sample_size(self.format))
            waveFile.setframerate(self.rate)
            waveFile.writeframes(b''.join(self.audio_frames))
            waveFile.close()
        print("\n\n\n\naudio stopped\n\n\n\n")
        pass

    # Launches the audio recording function using a thread
    def start(self):
        audio_thread = threading.Thread(target=self.record)
        audio_thread.start()





def start_AVrecording(filename):
    print(threading.enumerate())

    global video_thread
    global audio_thread

    video_thread = VideoRecorder()
    audio_thread = AudioRecorder()

    audio_thread.start()
    video_thread.start()

    return filename




def start_video_recording(filename):

    global video_thread

    video_thread = VideoRecorder()
    video_thread.start()

    return filename


def start_audio_recording(filename):

    global audio_thread

    audio_thread = AudioRecorder()
    audio_thread.start()

    return filename




def stop_AVrecording(filename):
    if True:#keyboard.is_pressed('esc'):
        print(threading.enumerate())
        initialthread=threading.active_count()
        print("stopping av recording") 
        print(threading.active_count())
        print("stopping a recording") 
        if audio_thread.open!=True:
            initialthread=initialthread-1
        else:
            audio_thread.stop() 
        

        print(threading.active_count())
        frame_counts = video_thread.frame_counts
        elapsed_time = time.time() - video_thread.start_time
        recorded_fps = frame_counts / elapsed_time
        print( "total frames " + str(frame_counts))
        print( "elapsed time " + str(elapsed_time))
        print( "recorded fps " + str(recorded_fps))
        print("stopping v recording") 
        video_thread.stop() 
        print("vc stopped")
        print(threading.active_count())
        finalthread=threading.active_count()
        chthr=initialthread-finalthread

        # Makes sure the threads have finished
        while chthr!=2:#threading.active_count() > 1:
            print("sleeping")
            time.sleep(1)


#    Merging audio and video signal

    if abs(recorded_fps - 24) >= 0.01:    # If the fps rate was higher/lower than expected, re-encode it to the expected

        print( "Re-encoding")
        cmd = "ffmpeg -r " + str(recorded_fps) + " -i temp_video.avi -pix_fmt yuv420p -r 6 temp_video2.avi"
        subprocess.call(cmd, shell=True)

        print( "Mixing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video2.avi -pix_fmt yuv420p " + filename + ".avi"
        subprocess.call(cmd, shell=True)

    else:

        print( "Normal recording\nMixing")
        cmd = "ffmpeg -ac 2 -channel_layout stereo -i temp_audio.wav -i temp_video.avi -pix_fmt yuv420p " + filename + ".avi"
        subprocess.call(cmd, shell=True)

        print( "..")




# Required and wanted processing of final files
def file_manager(filename):

    local_path = os.getcwd()

    if os.path.exists(str(local_path) + "/temp_audio.wav"):
        os.remove(str(local_path) + "/temp_audio.wav")

    if os.path.exists(str(local_path) + "/temp_video.avi"):
        os.remove(str(local_path) + "/temp_video.avi")

    if os.path.exists(str(local_path) + "/temp_video2.avi"):
        os.remove(str(local_path) + "/temp_video2.avi")


    if os.path.exists(str(local_path) + "/" + filename + ".avi"):
        os.remove(str(local_path) + "/" + filename + ".avi")

    if os.path.exists(str(local_path) + "/" + filename + ".wav"):
        os.remove(str(local_path) + "/" + filename + ".wav")
            


def ctrl(filename,length):
    file_manager(filename)
    start_AVrecording(filename)
    time.sleep(length)
    stop_AVrecording(filename)
    local_path = os.getcwd()
    os.rename(str(local_path) + "/temp_audio.wav",str(local_path) + "/"+filename+".wav")
    os.remove(str(local_path) + "/temp_video.avi")
    os.remove(str(local_path) + "/temp_video2.avi")
    return video_thread.frame_counts


#print("run\npress escape to end")
#i=0;
#for i in range(1000):
#    print("ad")

#print("end")