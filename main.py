import webbrowser
import speech_recognition as sr
import pyttsx3
import os
import subprocess
import datetime
import openai
import requests
from config import api_key, weather_api, quotes_api
import random
import numpy as np
import time
def get_weather(city, api_key):
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        'key': api_key,
        'q': city
    }
    response = requests.get(base_url, params=params)
    return response.json()
chats = ""

def chat(query):
    global chats
    print(chats)
    openai.api_key = api_key
    chats += f"Chai: {query}\n Iris: "
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": chats}
            ],
            max_tokens=1024,
            top_p=1,
            temperature=0.7,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        message = response.choices[0].message['content']
        say(message)
        chats += message
        return message

    except openai.error.RateLimitError:
        say("Sorry, I have exceeded my quota for now. Please try again later.")
        return "Quota exceeded"
    except openai.error.InvalidRequestError as e:
        say(f"Invalid request: {str(e)}")
        return str(e)
    except Exception as e:
        say(f"An error occurred: {str(e)}")
        return str(e)

def get_quote_from_ninjas():
    url = "https://api.api-ninjas.com/v1/quotes"
    headers = {
        'X-Api-Key': quotes_api
    }
    response = requests.get(url, headers=headers)
    return response.json()

def say(text):
    engine = pyttsx3.init()


    voices = engine.getProperty('voices')


    for voice in voices:
        if 'zira' in voice.name.lower() or 'zira' in voice.id.lower():
            engine.setProperty('voice', voice.id)
            break
    else:
        print("No female voice found. Using default voice.")


    engine.setProperty('rate', 150)

    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
        try:
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"You said: {query}")
            return query
        except Exception as e:
            print("Sorry, I didn't get that. Please say again.")
            return ""

def open_spotify():
    path = r"C:\Users\chaithanya\AppData\Roaming\Spotify\Spotify.exe"
    if os.path.exists(path):
        subprocess.Popen([path])  # Adjust the path as necessary
    else:
        webbrowser.open("https://www.spotify.com")

if __name__ == "__main__":
    say("Iris A.I.")
    while True:
        query = take_command().lower()  # convert to lower case once here

        sites = [
            ["youtube", "https://www.youtube.com"],
            ["wikipedia", "https://www.wikipedia.org"],
            ["google", "https://www.google.com"],
            ["facebook", "https://www.facebook.com"]
        ]

        for site in sites:
            if f"open {site[0]}" in query:
                say(f"Opening {site[0]}...")
                webbrowser.open(site[1])

        if "the time" in query:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            say(f"The time is {current_time}")

        elif "open vs code" in query:
            path = r"C:\Users\Chaithanya\AppData\Local\Programs\Microsoft VS Code\Code.exe"
            if os.path.exists(path):
                subprocess.Popen([path])

        elif "play music" in query:
            path = r"C:\Users\Chaithanya\Desktop\Spotify.app"
            if os.path.exists(path):
                subprocess.Popen([path])
            else:
                open_spotify()

        elif "weather in" in query:
            city = query.split("in")[-1].strip()
            weather_data = get_weather(city, weather_api)

            if 'error' not in weather_data:
                weather_info = (
                    f"The current weather in {weather_data['location']['name']} is {weather_data['current']['condition']['text']} "
                    f"with a temperature of {weather_data['current']['temp_c']} degrees Celsius. "
                    f"Enjoy your day in {weather_data['location']['name']}!"
                )
                say(weather_info)
                print(weather_info)

        elif "say a quote" in query:
            quote_data = get_quote_from_ninjas()

            if quote_data:
                quote = quote_data[0]['quote']
                author = quote_data[0]['author']
                quote_info = f"{quote} by {author}"
                say(quote_info)
                print(quote_info)
            else:
                error_message = "Sorry, I couldn't fetch a quote right now."
                say(error_message)
                print(error_message)

        elif "goodbye iris" in query:
            say("Goodbye!")
            exit()

        elif "reset" in query:
            chats = ""
        else:
            print("Chatting....")
            chat(query)
