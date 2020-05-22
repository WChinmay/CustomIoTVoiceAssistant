# Record audio while button is pressed

#!/usr/bin/python
import RPi.GPIO as GPIO

import pyaudio
import wave
import time
 
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 512
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "rec41000.wav"
 
p = pyaudio.PyAudio()

#audio_info = p.get_device_info_by_index(0)
#print (audio_info)
 
#GPIO pin setup for button
ledPin = 18
buttonPin = 23

#set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#enable LED and button (button with pull-up)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#set LED to OFF
GPIO.output(ledPin, GPIO.LOW)

while(True):

	print "waiting for button event"

	#wait for button to be pressed
	time.sleep(0.2)
	GPIO.wait_for_edge(buttonPin, GPIO.FALLING)

	while True:
		try:
                    frames = []
                    stream = p.open(format = FORMAT,
                                            channels = CHANNELS, 
                                            rate = RATE, 
                                            input = True,
                                            frames_per_buffer = CHUNK)
            
                    print "* recording"
                    #turn on LED ring when recording starts
                    GPIO.output(ledPin, GPIO.HIGH)
            
                    #record as long as button held down
                    while GPIO.input(buttonPin) == 0:
                        data = stream.read(CHUNK)
                        frames.append(data)
            
                        break
            
                except IOError:
                        printer.println(textWrapped('- Aufnahmefehler. Starte neu, Moment bitte. -', 32))

	# button released
	print "* done"
	GPIO.output(ledPin, GPIO.LOW)

	stream.stop_stream()
	stream.close()
	p.terminate()

	#make wave file from recorded data stream
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()      