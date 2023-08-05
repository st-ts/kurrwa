# Simple test program which listens to a wake word
# and after detecting it turns on LED

import RPi.GPIO as GPIO
import time
import pvporcupine as porcu
import sounddevice as sd
import numpy as np
import pyaudio
import speech_recognition as sr
import requests
import pyttsx3
from flux_led import WifiLedBulb
from bs4 import BeautifulSoup

# Set the pins
GPIO.setmode(GPIO.BCM)
pin_led = 14
GPIO.setup(pin_led, GPIO.OUT)




# Set the wake word to smth for now
pico_key_path = '/home/stetsenko/macode/pico_pico.txt'
with open(pico_key_path, "r") as file:
    pico_key = file.read()
print('hey1')
# wake_word_path = "/home/stetsenko/.local/lib/python3.9/site-packages/pvporcupine/resources/keyword_files/raspberry-pi/porcupine_raspberry-pi.ppn"
model_path_pl = "/home/stetsenko/.local/lib/python3.9/site-packages/pvporcupine/lib/common/porcupine_params_pl.pv"

porcupine = porcu.create(keywords=['hej-kurwa'], access_key = pico_key, model_path = model_path_pl)

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


def control_bulbs(command):
    speak("Let the bulb shine")
    if "bed" in command:
        bulb_ip = '192.168.88.23'
    else:
        print("default is bed")
        bulb_ip = '192.168.88.23'
    bulb = WifeLedBulb(bulb_ip)
    bulb.setRgb(1,0,0)
    #flux_led bulb_ip -w 75 -1




turn_on_led(pin_led)
sd.sleep(3)
turn_off_led(pin_led)

# Function to fetch the current temperature
def get_current_temperature(location):
    url = f"https://weather.com/en-IN/weather/today/l/{location}"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        temperature = soup.find("span", {"data-testid": "TemperatureValue"}).text
        return temperature
    else:
        return None

# Function to recognize speech after the wake word
def recognize_command():
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
        return ' '


# Function to speak out the given text
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

        # Set other voice properties for a funny effect (if available)
        # For example, you can adjust the pitch and rate of speech
        engine.setProperty('rate', 95)  # Slower speech rate
        engine.setProperty('pitch', 10)  # Higher pitch for a funny voice

    engine.say(text)
    engine.runAndWait()



while True:
  audio_frame = get_next_audio_frame()
  keyword_index = porcupine.process(audio_frame)

  if keyword_index == 0:
      print("hej kurwa")
      speak_polish("Ja pierdolę")
      kurrwa_led_greet(pin_led)
      command_detected = False
      while not command_detected:
          audio_frame = get_next_audio_frame()
          command = recognize_command()
          command_led_on = "turn on"
          command_led_off = "turn off"
          go_weather = "weather"
          stop_listen = "goodbye"
          location = "07029"
          if command:
            if command_led_on in command:
                print("Command detected")
                turn_on_led(pin_led)
                audio_frame = np.array([], dtype=np.int16)
            elif command_led_off in command:
                print("Command detected")
                turn_off_led(pin_led)
                audio_frame = np.array([], dtype=np.int16)
            elif go_weather in command:
                print("Fetching the weather data")
                temperature = get_current_temperature(location)
                if temperature:
                    temp_info = f"The current temperature is {temperature}C."
                    print(temp_info)
                    # speak(temp_info)
                    speak_funny(temp_info)
                else:
                    print("Failed to fetch weather data.")
            elif stop_listen in command:
                command_detected = True
                speak_polish("jyake bydło jebane")
            elif "shine" in command:
                control_bulbs(command)
            else:
                speak_funny(command)
                




porcupine.delete()
