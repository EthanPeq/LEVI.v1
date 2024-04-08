import requests
import json

import sys
import threading

import pyaudio
from vosk import Model, KaldiRecognizer

import pyttsx3



url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}


    

prompt = ""

## ------------ Setting up Text to Speech -------------
engine = pyttsx3.init()

def text_to_speech(text):
    #-- Using pyttsx3 --
    engine.say(text)
    engine.runAndWait()

def run_assistant():

    ## ------------ Setting up Speech Recognizer -----------
    model = Model(r"C:\Users\11soc\OneDrive\Desktop\LEVI.v1\vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    ## ------------- Listening for keyword ------------------
    print("say something")
    while True:
        data=stream.read(8192)
        text = ""
        if recognizer.AcceptWaveform(data):
            text=recognizer.Result()
            text.lower()
            text = text[14:-3]
            print(text)


        if "hey" in text:
            if "stop" in text:
                print("bye")
                sys.exit()
            
            #-- cleaning STT output
            if "we've i" in text:
                text = text[11:]
            elif "we were" in text:
                text = text[11:]
            elif "we have i" in text:
                text = text[13:]
            else:
                text = text[9:]
            print(text)

            #-- sending input to the Mistral Model --
            prompt =  "Your name is Levi. Now, let's discuss, in one sentence: " + text
            data = {
                "model": "mistral",
                "stream": False,
                "prompt": prompt
            }

            response = requests.post(url, headers=headers, data=json.dumps(data))

            if response.status_code == 200:
                response_text = response.text
                data = json.loads(response_text)
                actual_response = data["response"]
                print(actual_response)
                text_to_speech(actual_response)
                print("worked")
            else:
                print("Error:", response.status_code, response.text)
#-----------------------------------------------------------------------------
            

threading.Thread(target=run_assistant()).start()
