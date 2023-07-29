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

def kurrwa_led_greet(some_led):
    for i in [1,2,3]:
        turn_on_led(some_led)
        sd.sleep(100)
        turn_off_led(some_led)
        sd.sleep(200)


turn_on_led(pin_led)
sd.sleep(3)
turn_off_led(pin_led)


def recognize_commgjand(audio_frame):
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


while True:
  audio_frame = get_next_audio_frame()
  keyword_index = porcupine.process(audio_frame)

  if keyword_index == 0:
      print("hej kurwa")
      kurrwa_led_greet(pin_led)
      command_detected = False
      while not command_detected:
          audio_frame = get_next_audio_frame()
          command = recognize_command()
          command_led_on = "turn on"
          command_led_off = "turn off"
          if command:
            if command_led_on in command:
                print("Command detected")
                turn_on_led(pin_led)
                audio_frame = np.array([], dtype=np.int16)
            elif command_led_off in command:
                print("Command detected")
                turn_off_led(pin_led)
                audio_frame = np.array([], dtype=np.int16)




porcupine.delete()