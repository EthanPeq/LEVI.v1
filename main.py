import requests
import json

import sys
import threading

import pyaudio
from vosk import Model, KaldiRecognizer

import pyttsx3

import pygame

import time


## ------------ Setting up Ollama LLM -------------
url = "http://localhost:11434/api/generate"

headers = {
    'Content-Type': 'application/json',
}
 ## sending in an empty request to preload the model
response = requests.post(url, headers=headers, data=json.dumps({"model": "mistral",}))

## ------------ Setting up Text to Speech -------------
engine = pyttsx3.init()

def text_to_speech(text):
    #-- Using pyttsx3 --
    engine.say(text)
    engine.runAndWait()

def keywordSearch(text):
    if text == "":
        return text, False
    
    validKeyword = False
    #-- cleaning STT output by looking for keyword
    if "hey levi" in text:
        text = text[8:]
        validKeyword = True        
    elif "hey i" in text or "haley" in text:
        text = text[5:]
        validKeyword = True
    elif "hayley" in text:
        text = text[6:]
        validKeyword = True     
    elif "helluva" in text or "however" in text or "here i" in text or "tell me" in text:
        text = text[7:]
        validKeyword = True
    elif "hermes i" in text:
        text = text[8:]
        validKeyword = True    
    elif "we have i" in text or "haley's i" in text or "heroes i" in text:
        text = text[9:]
        validKeyword = True            
    elif "hey with i" in text or "hey look i" in text or "hurry and i" in text or "her lawyer" in text or "hey we die" in text or "harry" in text or "henry" in text: 
        text = text[10:]
        validKeyword = True    
    elif "hey we've i" in text or "hey we were" in text or "hey would i" in text or "hey leave i" in text or "hey we like" in text or "hello there" in text or "haley right" in text:
        text = text[11:]
        validKeyword = True    
    elif "he'll move i" in text :
        text = text[12:]
        validKeyword = True    
    elif "he'll leave i" in text or "hey knew that" in text:
        text = text[13:]
        validKeyword = True     
    else:
        if "hey" in text:
            text = text[9:]
            validKeyword = True

    print("validKeyword in keywordSearch: " + str(validKeyword))

    return validKeyword, text

def playMusic():
    pygame.mixer.init()
    pygame.mixer.music.load("Craft-Sale-Song.wav")
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    print("song finished")

def run_assistant():

    ## --------------------- Introduction ------------------
    text_to_speech("Hello, my Name is Levi. Happy to assist you!")

    ## ------------ Setting up Speech Recognizer -----------
    model = Model(r"/home/epequign/Desktop/Levi/LEVI.v1/vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    ## ------------- Listening for keyword ------------------
    print("say something")
    listening = True
    validKeyword = False
    while True:
        text = ""
        data=stream.read(8192)
        if listening:
            if recognizer.AcceptWaveform(data):
                text=recognizer.Result()
                text.lower()
                text = text[14:-3]
                print("OG Text:" +text+".")
                validKeyword,text = keywordSearch(text)
                if validKeyword is True:
                    listening = False
                    stream.stop_stream()


        if validKeyword is True:
            text_to_speech("Understood!")
            print("prompt:  " +text)
            if "stop" in text:
                print("bye")
                sys.exit()


            # -- filtering through commands --
            # - play music -
            if "play music" in text or "played music" in text:
                text_to_speech("Playing the greatest song ever!")
                time.sleep(1)
                playMusic()

            else:
                #-- sending input to the Mistral Model --
                prompt =  "Your name is Levi. Lets continue to discuss. In one sentence: " + text
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
                else:
                    print("Error:", response.status_code, response.text)
                    
            listening = True
            validKeyword = False
            stream.start_stream()
#-----------------------------------------------------------------------------       
threading.Thread(target=run_assistant()).start()
