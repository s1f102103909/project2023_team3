from django.test import TestCase

# Create your tests here.
import os
import openai
import pyttsx3
import pyaudio
import wave
import numpy as np
import time
import audioop
from gtts import gTTS
import speech_recognition as sr
import tempfile
import pygame

from playsound import playsound
from io import BytesIO
import whisper

import requests, json
import io

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='glossy-aloe-396205-d7fdd774bdbe.json'

API_KEY = "7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw"
API_BASE = "https://api.openai.iniad.org/api/v1"

def generate_answer(prompt):
    openai.api_key = API_KEY
    openai.api_base = API_BASE
    openai.Model.list() #OpenAIのインスタンスを生成
    
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {'role':'user', 'content':prompt}
        ],
        temperature = 0,
        max_tokens = 1024,
        top_p = 1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response['choices'][0]['message']['content']
    return answer

def text_to_speech(response):
    engine = pyttsx3.init()
    engine.setProperty("rate", 100)
    engine.say("{}".format(response))
    engine.runAndWait()

def forAText():
  openai.api_key = os.getenv('234beG84Ybh7BeumEJr6kfmjPSulkprNO9a_BRS89Ai922HJmqVkS7RYt29B3r_YtvnTcegVG7Jczx06iQ6cHzw')

  #音声認識オブジェクト生成
  r = sr.Recognizer()

  #マイクから音声を取得
  with sr.Microphone() as source:
      print("何か話してください")
      audio = r.listen(source)

  try:
      #音声をテキストに変換
      user_input = r.recognize_google(audio, language='ja-JP')
      print(f"あなた：{user_input}")

      # openaiのAPIに連携
      response = openai.Completion.create(
          engine = "text-davinci-002",
          prompt = user_input,
          temperature = 0.5,
          max_tokens = 100
      )

      ai_response = response.choices[0].text.strip()
      print(f"AI: {ai_response}")

      #テキストを音声に変換
      tts = gTTS(text = ai_response, lang='ja')
      with tempfile.NamedTemporaryFile(delete=True) as fp:
          tts.save(f"{fp.name}.mp3")
          pygame.mixer.init()
          pygame.mixer.music.load(f"{fp.name}.mp3")
          pygame.mixer.music.play()
          while pygame.mixer.music.get_busy():
              pygame.time.Clock().tick(10)
  except sr.UnknownValueError:
      print("Google Speech Recognitionは音声を理解できませんでした")
  except sr.RequestError as e:
      print(f"Google Speech Recognitionサービスからの結果を要求できませんでした;{e}")


class Voicevox:
    def __init__(self,host="127.0.0.1",port=50021):
        self.host = host
        self.port = port

    def speak(self,text=None,speaker=47): # VOICEVOX:ナースロボ＿タイプＴ

        params = (
            ("text", text),
            ("speaker", speaker)  # 音声の種類をInt型で指定
        )

        init_q = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )

        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )

        # メモリ上で展開
        audio = io.BytesIO(res.content)

        with wave.open(audio,'rb') as f:
            # 以下再生用処理
            p = pyaudio.PyAudio()

            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, pyaudio.paContinue)

            stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True,
                            stream_callback=_callback)

            # Voice再生
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            p.terminate()