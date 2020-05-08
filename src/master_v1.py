import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import pyaudio # To record from microphone
import wave # To save as .wav file

# Consider implementation of having a main loop that does the recording based on a bool set in the the two callbacks
# to be true or false.
# Or consider using while(pressed) logic and break recording when not pressed anymore. 

def record_audio():
    form_1 = pyaudio.paInt16 # 16-bit resolution
    chans = 1 # 1 channel
    samp_rate = 44100 # 44.1kHz sampling rate
    chunk = 4096 # 2^12 samples for buffer
    record_secs = 8 # seconds to record
    dev_index = 2 # device index found by p.get_device_info_by_index(ii), might need some tweaking to have functional everytime
    wav_output_filename = 'interim.wav' # name of .wav file

    audio = pyaudio.PyAudio() # create pyaudio instantiation

    # create pyaudio stream
    stream = audio.open(format = form_1, rate = samp_rate, channels = chans, \
                        input_device_index = dev_index, input = True, \
                        frames_per_buffer=chunk)
    print("Started recording audio from Microphone")
    frames = []

    # loop through stream and append audio chunks to frame array
    for ii in range(0, int((samp_rate/chunk) * record_secs)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finished recording audio from Microphone")

    # stop the stream, close it, and terminate the pyaudio instantiation
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # save the audio frames as .wav file
    wavefile = wave.open(wav_output_filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()


def button_press_callback(channel):
    print("Button was pushed!")
    record_audio()
    

def button_release_callback(channel):
    print("Button was released!")

# GPIO Button Stuff
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

GPIO.add_event_detect(10, GPIO.RISING, callback=button_press_callback) # Setup event on pin 10 rising edge
GPIO.add_event_detect(10, GPIO.FALLING, callback=button_release_callback) # Setup event on pin 10 falling edge


message = input("Press enter to quit\n\n") # Run until someone presses enter
# Cleanup GPIO Button stuff
GPIO.cleanup() # Clean up