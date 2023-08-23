# Thid module stores functions related to different commands


import RPi.GPIO as GPIO
import time, datetime
import pvporcupine as porcu
import sounddevice as sd
import numpy as np
import pyaudio
import re
import speech_recognition as sr
import requests
import pyttsx3
import pygame
import webcolors

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
# based on the text of command given

def identify_actions(command_text):
    command_text = command_text.lower()
    # if at least 1 command idenified, don't start mocking
    command_identified = False
    
    # all the actions related to light 
    if "light" in command_text:fghfhggghjjhg
        implement_light(command_text)
        command_identified = True
    
    # all the actions related to weather (different words can trigger this)
    weather_words = ["temperature", "uv index", "weather", "rain"]
    for word in weather_words:
        if word in command_text: 
            print("gonna get you the weather")
            implement_weather(command_text)
            command_identified = True
            break
    
    # Setting a timer
    if "timer" in command_text:
        set_timer(command_text)
        command_identified = True
    
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
def play_sound(sound_path, volume=0.3):
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

def set_timer(command):
    match = re.search(r'\d+', command)
    if match:
        minutes = int(match.group())
        speak_funny("Timer for " + str(minutes) + " minutes starts")
        timer_start = datetime.datetime.now()
        time_over = False
        while not time_over:
            time_now = datetime.datetime.now()
            if time_now > timer_start + datetime.timedelta(seconds=minutes*60):
                time_over = True

        speak_funny("time is over")
        for i in [0,0,0]:
            speak("beep beep beep")
            time.sleep(0.5)
    else:
        speak_funny("You did not say for how long")


#
def implement_light(command):
    # inform that the command went through
    speak_funny("Setting the light")
    bed_ip = "192.168.88.23";
    top_door_ip = "192.168.88.13";
    top_paint_ip = "192.168.88.14";
    top_wind_ip = "192.168.88.16";
    top_book_ip = "192.168.88.15";
    bulb_ips = {"bed": [bed_ip], "door": [top_door_ip],
                "paint": [top_paint_ip], "windor": [top_wind_ip],
                "book": [top_book_ip], "ceiling": 
                    [top_door_ip,top_paint_ip,top_wind_ip,top_book_ip],
                    "all": [top_door_ip,top_paint_ip,top_wind_ip,top_book_ip,bed_ip]}
    
    # determine the scope of the bulbs used
    # if a certain bulb is mentioned, it will be added tp the scope
    # default is all the lights
    bulbs_to_set = []
    for bulb in bulb_ips.keys():
        if bulb in command:
            bulbs_to_set.extend(bulb_ips[bulb])
            break
        else:
            
    if bulbs_to_set == []:
        print("default is all")
        bulbs_to_set.extend(bulb_ips["all"])
            

    
    # Determine if within the command any color is mentioned
    command_words = command.split(" ")
    for bulb_ip in bulbs_to_set:
        bulb = WifiLedBulb(bulb_ip)
        if "of" in command:
            bulb.turnOff()
        elif "warm" in command:
            bulb.setWarmWhite(100)
        elif "on" in command:
            bulb.turnOn()
        else:
            for word in command_words:
                if is_word_color(word):
                    [r,g,b] = webcolors.name_to_rgb(word)
                    bulb.setRgb(r,g,b)
                    break
                    
        # Change light intensity
        if "dark" in command:
            bulb.set_levels(brightness=30)
        elif "bright" in command:
            bulb.set_levels(brightness=100)
            
                
    



# Check if some word is a color
def is_word_color(word):
    try:
        webcolors.name_to_rgb(word)
        return True
    except ValueError:
        return False


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
        
        
# The weather related
def implement_weather(command):
    print("Fetching the weather data")
    
    # Check if location is mentioned ADD later
    if "in" in command:
        command_words = command.split(" ")
    else:
        location = "07029"
        
        
    
    temperature = get_current_temperature(location)
    if temperature:
        temp_info = f"The current temperature is {temperature}C."
        print(temp_info)
        # speak(temp_info)
        speak_funny(temp_info)
    else:
        print("Failed to fetch weather data.")


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

