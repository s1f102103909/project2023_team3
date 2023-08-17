from django.test import TestCase

# Create your tests here.
import os
import openai
import gtts
from playsound import playsound
from io import BytesIO

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
    # file を保存してから音声を流す
    # text入力 -> tts(音声ファイル)
    #tts = gtts.gTTS("hello world",lang="en") # Janpanese : ja;
    # 音声ファイル保存
    #tts.save("/soundfile/hello.mp3")
    # play
    #playsound("/soundfile/hello.mp3")

    # 音声を直接流す
    mp3_fp = BytesIO()
    tts = gtts.gTTS("{0}".format(response),lang="ja")
    tts.write_to_fp(mp3_fp)
