# This code listens to the wake word, and maybe later I will make a 
# module which processes the commands and executes them


import RPi.GPIO as GPIO
import time, datetime
import pvporcupine as porcu
import sounddevice as sd
import numpy as np
import pyaudio
import speech_recognition as sr
import requests
import pyttsx3
import pygame
import threading
import commands
from flux_led import WifiLedBulb
from bs4 import BeautifulSoup

# Specify paths to audios
ja_pierdole = 'sounds/ja_pierdole.mp3' 
jake_bydlo = 'sounds/jake_bydlo_jebane.mp3'
gandalf_greet = 'sounds/gandalf-im-trying-to-help-you.mp3'
gandalf_bye = 'sounds/gandalf-things-are-now-in-motion-that-cannot-be-undone.mp3'

# Set the pins
GPIO.setmode(GPIO.BCM)
pin_led = 14
GPIO.setup(pin_led, GPIO.OUT)


# Set the wake word to "Hej kurwa"
pico_key_path = '/home/stetsenko/macode/pico_pico.txt'
with open(pico_key_path, "r") as file:
    pico_key = file.read()
print('hej')
model_path_pl = "/home/stetsenko/.local/lib/python3.9/site-packages/pvporcupine/lib/common/porcupine_params_pl.pv"

porcupine = porcu.create(keywords=['hej-kurwa'], access_key = pico_key, model_path = model_path_pl)
gandalf_model = porcu.create(keywords=['my-dearest-friend'], access_key = pico_key)

# Define audio settings
sample_rate = 16000  # Sample rate in Hz
frame_length = 512   # Frame length in number of samples

# Create an instance of PyAudio
audio_interface = pyaudio.PyAudio()

# Open the microphone stream
stream = audio_interface.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=sample_rate,
    frames_per_buffer=frame_length,
    input=True
)

def play_sound(sound_path, volume=1):
    # Initialise, load, play and exit
    pygame.mixer.init()
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue
    pygame.mixer.quit()
    

def get_next_audio_frame():
    audio_frame = stream.read(frame_length)
    return np.frombuffer(audio_frame, dtype=np.int16)

def turn_on_led(some_led):
    GPIO.output(some_led, GPIO.HIGH)

def turn_off_led(some_led):
    GPIO.output(some_led, GPIO.LOW)

def kurrwa_led_greet(some_led):
    turn_on_led(some_led)
    sd.sleep(100)
    turn_off_led(some_led)
    sd.sleep(200)



# Function to recognize speech after the wake word
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something...")
        audio = recognizer.listen(source)

    try:
        recognized_text = recognizer.recognize_google(audio, language="en-US")
        print(recognized_text)
        return recognized_text

    except sr.UnknownValueError:
        print("Speech could not be recognized.")
        return None


# Functions to speak out the given text
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    
def speak_polish(text):
    engine = pyttsx3.init()
    engine.setProperty('voice', 'polish')
    engine.say(text)
    engine.runAndWait()
    
    
    
# Function to speak out the given text with a funny voice
def speak_funny(text):
    engine = pyttsx3.init()

    # Get a list of available voices
    voices = engine.getProperty('voices')

    # Select a funny voice (the voice index may vary depending on your system)
    funny_voice_index = 1

    if len(voices) > funny_voice_index:
        # Set the selected voice
        engine.setProperty('voice', voices[funny_voice_index].id)

        # Set other voice properties for a funny effect like pitch and rate of speech
        engine.setProperty('rate', 95)  # Slower speech rate
        engine.setProperty('pitch', 10)  # Higher pitch for a funny voice

    engine.say(text)
    engine.runAndWait()
listen_time_sec = 15


# Main loop monitoring the wake word and identifying the speech after it
while True:
    audio_frame = get_next_audio_frame()
    kurrwa_index = porcupine.process(audio_frame)
    gandalf_index = gandalf_model.process(audio_frame)
    start_listen = False
    
    if kurrwa_index == 0:
        print("hej kurwa")
        play_sound(ja_pierdole,1)
        assitant_character = "kurrwa"
        start_listen = True
    elif gandalf_index == 0:
        print("Gandalf awoken")
        play_sound(gandalf_greet, 1)
        assitant_character = "gandalf"
        start_listen = True
        
    if start_listen:
      # Set the time after which the listening stops
      time_now = datetime.datetime.now() 
      stop_listen_time = time_now + datetime.timedelta(seconds=listen_time_sec)
      
      
      kurrwa_led_greet(pin_led)
      listen_for_command = True
      while listen_for_command:
          
          # Check if the program was listening for too long
          time_now = datetime.datetime.now() 
          if stop_listen_time < time_now:
              if assitant_character == "kurrwa":
                  play_sound(jake_bydlo,1)
              else:
                  play_sound(gandalf_bye,1)
              listen_for_command = False
              print("stopped listening")
          else:
              # Get audiodata and send it to the speech recognizer
              audio_frame = get_next_audio_frame()
              user_speech = recognize_speech()
              
              # If speech is detected, reset the listen timer and pass the 
              # command to the commands module using a thread for parallel 
              if user_speech:
                  
                      
                  stop_listen_time = datetime.datetime.now() + datetime.timedelta(seconds=listen_time_sec)
                
                  execute_command = threading.Thread(target=commands.identify_actions,
                                  args=(user_speech,))
                  execute_command.start()
                  
                  if "goodbye" in user_speech:
                      if assitant_character == "kurrwa":
                        play_sound(jake_bydlo,0.7)
                      else:
                        play_sound(gandalf_bye,0.7)
                      listen_for_command = False
                      print("stopped listening")
                      break




porcupine.delete()
