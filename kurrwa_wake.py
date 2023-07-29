# Simple test program which listens to a wake word
# and after detecting it turns on LED

import RPi.GPIO as GPIO
import time
import pvporcupine as porcu
import sounddevice as sd
import numpy as np
import pyaudio
import speech_recognition as sr


# Set the pins
GPIO.setmode(GPIO.BCM)
pin_led = 14
GPIO.setup(pin_led, GPIO.OUT)


# Set the wake word to smth for now
pico_key_path = '/home/stetsenko/macode/pico_pico.txt'
with open(pico_key_path, "r") as file:
    pico_key = file.read()

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

def recognize_command(audio_frame):
    global sample_rate
    recognizer = sr.Recognizer()
    audio_source = sr.AudioData(audio_frame.tobytes(),
                                sample_rate=sample_rate, sample_width = 2)

    try:
        # Use the recognizer to perform the speech recognition
        recognized_text = recognizer.recognize_google(audio_source, language="en-US")
        return recognized_text.lower()
    except sr.UnknownValueError:
        return None

    audio_text = audio_frame.lower()
    command = "turn on"
    if command in audio_text:
        return True
    else:
        return False

while True:
  audio_frame = get_next_audio_frame()
  keyword_index = porcupine.process(audio_frame)

  if keyword_index == 0:
      print("hej kurwa")
      command_detected = False
      while not command_detected:
          audio_frame = get_next_audio_frame()
          command = recognize_command(audio_frame)
          my_command = "turn on"
          if command:
            if my_command in command:
                print("Command detected")
                turn_on_led(pin_led)




porcupine.delete()