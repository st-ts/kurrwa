# Thid module stores functions related to different commands


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

from flux_led import WifiLedBulb
from bs4 import BeautifulSoup

# Specify paths to audios
ja_pierdole = 'sounds/ja_pierdole.mp3' 
jake_bydlo = 'sounds/jake_bydlo_jebane.mp3'

# Set the pins
GPIO.setmode(GPIO.BCM)
pin_led = 14
GPIO.setup(pin_led, GPIO.OUT)


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

# Main if {word} function for idenifing which actions should be implemented 
# based on text of command given

def identify_actions(command_text):
    # if at least 1 command idenified, don't start mocking
    command_identified = False
    
    # all the actions related to light 
    if "light" in command_text:
        implement_light(command_text)
        command_identified = True
    
    # all the actions related to weather (different words can trigger this)
    weather_words = ["temperature", "uv index", "weather", "rain"]
    for word in weather_words:
        if word in command: 
            implement_weather(command)
            command_identified = True
            break
        
    # to add later, spotify
    music_words = ["spotify", "play", "music", "song"]
    for word in music_words:
        if word in command_text:
            implement_music(command_text)
            command_identified = True
            break
            
    # add later: integration with tasks
    
    # add later: integration with calendar (maybe 1 function with tasks)
    
    # add later: chat with different characters
            
    
    
# not for music, but for playing pre-made recordings of responces
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

# for indicator leds
# set brightness
def set_brightness_led(led_pin, brightness):
    pass 

# turn on
def turn_on_led(some_led):
    GPIO.output(some_led, GPIO.HIGH)

# turn off
def turn_off_led(some_led):
    GPIO.output(some_led, GPIO.LOW)



def implement_light(command):
    # inform that the command went through
    speak("Setting the light")
    
    bulbs = {"bed": "192.168.88.23", "mirror": 1, "ceiling": None}
    
    # determine the scope of the bulbs used
    # if a certain bulb is mentioned, it will be the only one set
    for bulb in bulb_ips.keys():
        if bulb in command_text:
            bulb_ip = bulb_ips(bulb)
        else:
            print("default is bed")
            bulb_ip = '192.168.88.23'
            
            
    
    
    bulb = WifiLedBulb(bulb_ip)
    
    # Implement an action based on the command
    if "red" in command:
        bulb.setRgb(1,0,0)
    elif "warm" in command:
        bulb.setWarmWhite(100)
    elif "green" in command:
        bulb.setRgb(0,1,0)
    elif "of" in command:
        bulb.turnOff()
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

