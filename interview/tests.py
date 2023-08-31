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

def start():
    # ボタンを押すなどのイベントがない場合は一定時間後に自動で録音を開始
    N = 5  # 無音検出時間（秒）
    THRESHOLD = 2000  # 音量のしきい値

    # 音声録音関係のパラメータ
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 2**11
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "file.wav"

    iAudio = pyaudio.PyAudio()

    # 録音開始
    stream = iAudio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        rms = audioop.rms(data, 2)  # 音量の取得
        if rms < THRESHOLD:  # 音量がしきい値を下回ったらカウント開始
            time.sleep(N)
            rms = audioop.rms(stream.read(CHUNK), 2)
            if rms < THRESHOLD:  # N秒後もしきい値を下回っていたら録音終了
                break

    # 録音終了
    stream.stop_stream()
    stream.close()
    iAudio.terminate()

    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(iAudio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    return WAVE_OUTPUT_FILENAME

def speech_to_text(filePath):

    # 音声ファイルを開く
    audio_file= open(filePath, "rb")

    # Speech to Text変換
    response = openai.Audio.transcribe(
        api_key=API_KEY,
        model = 'whisper-1', # Speech-to-Textモデル
        file  = audio_file,  # オーディオファイル
        response_format = 'text',
    )
    
    os.remove(filePath)
    
    # 変換後のテキスト出力
    return response.text

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

forAText()