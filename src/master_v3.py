# Version 3 of master code, running in the background using a sysdaemon process on the RasPi

import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import pyaudio # To record from microphone
import wave # To save as .wav file
# Imports for STT
import json
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
import threading
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
# Imports for NLP
# import spacy
import nltk
from nltk.corpus import wordnet
# Imports for ElasticSearch
import os, base64, re, logging
from elasticsearch import Elasticsearch
# Imports for TTS
from subprocess import call
# from espeak import espeak


# Consider implementation of having a main loop that does the recording based on a bool set in the the two callbacks
# to be true or false.
# Or consider using while(pressed) logic and break recording when not pressed anymore. 

# Init for button
button_press_flag = 0

# Init for NLP
# nlp = spacy.load('en')
sentence = ""
query = ""
converted = {}
valid = set(("id", "name", "price", "size", "color", "description", 
             "first_name", "last_name", "address", "email_address", "phone_number", "other_details",
             "place", "shipped", "ship_via", "expected", "delivered", "shipping", "cost", 
             "item", "product", "status", "code", "quantity", "details", 
             "customer", "order")) # set of valid schema elements

# Init for ElasticSearch
outloud_answer = ""
# Using bonsai for now
# Log transport details (optional):
logging.basicConfig(level=logging.INFO)

# Parse the auth and host from env:
bonsai = 'redacted' # redacted for public repo
auth = re.search('https\:\/\/(.*)\@', bonsai).group(1).split(':')
host = bonsai.replace('https://%s:%s@' % (auth[0], auth[1]), '')
# optional port
match = re.search('(:\d+)', host)
if match:
    p = match.group(0)
    host = host.replace(p, '')
    port = int(p.split(':')[1])
else:
    port=443

# Connect to cluster over SSL using auth for best security:
es_header = [{
'host': host,
'port': port,
'use_ssl': True,
'http_auth': (auth[0],auth[1])
}]
# Instantiate the new Elasticsearch connection:
es = Elasticsearch(es_header)

# Verify that Python can talk to Bonsai (optional):
es.ping()

# Init for STT
authenticator = IAMAuthenticator('redacted') # redacted for public repo
service = SpeechToTextV1(authenticator=authenticator)
service.set_service_url('https://stream.watsonplatform.net/speech-to-text/api')

# Class Setup with modifiable callbacks for websockets
# ALTERNATE implementation using HTTP requests look at stt.py
# class MyRecognizeCallback(RecognizeCallback):
#     def __init__(self):
#         RecognizeCallback.__init__(self)

#     def on_transcription(self, transcript):
#         print("Here is the transcript")
#         print(transcript)
#         global sentence
#         sentence = transcript

#     def on_connected(self):
#         print('Connection was successful')

#     def on_error(self, error):
#         print('Error received: {}'.format(error))

#     def on_inactivity_timeout(self, error):
#         print('Inactivity timeout: {}'.format(error))

#     def on_listening(self):
#         print('Service is listening')

#     def on_hypothesis(self, hypothesis):
#         # print(hypothesis)
#         pass

#     def on_data(self, data):
#         # print(data)
#         pass


def convert_text_to_speech():
    # espeak.synth(outloud_answer)
    call(["espeak", "-s140 -ven+18 -z", outloud_answer])


def interact_with_elasticsearch():
    global outloud_answer
    print("This is the query")
    print(query)
    print("End of query")
    query_body = {"query": {"simple_query_string": {"fields": [], "query": query, "default_operator": "AND"}}}
    result = es.search(body=query_body)
    # Extract desired text from result into outloud_answer
    # Train to find the interested key/get from natural language query
    interested_key = 'product_price'
    print("Here is the result")
    print(result)
    print("End of result")
    # print(result['hits']['hits'][0]['_source'][interested_key])
    outloud_answer = "This is your answer"
    # outloud_answer = result['hits']['hits'][0]['_source'][interested_key]


def parse_nlp():
    global query
    tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
    # print(tagged)
    new_word = ""
    for (word,tag) in tagged:
        synonyms = []
        if tag == 'NN' or tag == 'NNS':
            for syn in wordnet.synsets(word):
                for l in syn.lemmas():
                    if l.name() in valid: new_word = l.name()
                    synonyms.append(l.name())
                    # print(set(synonyms))
            if new_word: converted[word] = new_word
            if query: query += ' '
            if new_word: query += new_word
            else: query += word
            new_word = ""
        if tag == 'NNP' or tag == 'NNPS':
            if query: query += ' '
            query += word
        # doc = nlp(sentence)
        # # print("The sentence is: ", sentence)
        # # print([ent for ent in doc.ents])
        # for ent in doc.ents: 
        #     if str(ent) not in query and str(ent) not in converted:
        #         if query: query += ' '
        #         query += str(ent)
        print("The ElasticSearch input is:", query)
        # print(converted)


def convert_speech_to_text():
    # Register mycallback as an object to be able to use the callback functions
    # mycallback = MyRecognizeCallback()
    # # open interim.wav as the audio file to be cnverted to text
    # audio_file = open(join(dirname(__file__), 'interim.wav'), 'rb')
    # audio_source = AudioSource(audio_file)
    # recognize_thread = threading.Thread(
    #    target=service.recognize_using_websocket,
    #    args=(audio_source, "audio/l16; rate=44100; smart_formatting=True", mycallback))
    # recognize_thread.start()
    global sentence
    with open(join(dirname(__file__), 'interim.wav'),
          'rb') as audio_file:
        blob = service.recognize(
            audio=audio_file,
            content_type='audio/wav',
            timestamps=False,
            word_confidence=False).get_result()
        sentence = blob['results'][0]['alternatives'][0]['transcript']
    print("Here is the sentence: {}", sentence)


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
        if GPIO.input(10) == GPIO.HIGH:     # record only if button is still pressed
            data = stream.read(chunk)
            frames.append(data)
        else:
            break       # break out and stop recording if the button has been released

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
    global button_press_flag
    # print("Button was pushed!")
    button_press_flag = 1
    # record_audio()
    # copy stuff after record_audio() here if implementation switches
    

def button_release_callback(channel):
    print("Button was released!")
    button_press_flag = 0

# GPIO Button Stuff
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

GPIO.add_event_detect(10, GPIO.RISING, callback=button_press_callback) # Setup event on pin 10 rising edge
# GPIO.add_event_detect(10, GPIO.FALLING, callback=button_release_callback) # Setup event on pin 10 falling edge


while(True): # Run until someone presses enter
    if button_press_flag == 1:
        button_press_flag = 0
        record_audio()
        convert_speech_to_text()
        parse_nlp()
        interact_with_elasticsearch()
        convert_text_to_speech()

# Cleanup GPIO Button stuff
GPIO.cleanup() # Clean up
