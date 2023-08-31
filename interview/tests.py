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
import gtts
from playsound import playsound
from io import BytesIO

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