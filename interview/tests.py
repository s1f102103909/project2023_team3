from django.test import TestCase

# Create your tests here.
import os
import pyaudio
import wave
import time
import requests, json
import io

import deepl

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='glossy-aloe-396205-d7fdd774bdbe.json'

speech_active = False

class Voicevox:
    def __init__(self,host="127.0.0.1",port=50021):
        self.host = host
        self.port = port

    def speak(self,text=None,speaker=13): # VOICEVOX:ナースロボ＿タイプＴ

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

    #日本語を英語に翻訳
def JP_To_EN(text):
    sourse_lang = 'JA'
    traget_lang = 'EN-US' # EN-GB

    translator = deepl.Translator('915e4495-52d5-1b86-a1f3-0d620ac62c20:fx')

    result = translator.translate_text(text, source_lang=sourse_lang,target_lang=traget_lang)
    
    return result.text

    #英語を日本語に翻訳
def EN_To_JP(text):
    sourse_lang = 'EN'
    traget_lang = 'JA'

    translator = deepl.Translator('915e4495-52d5-1b86-a1f3-0d620ac62c20:fx')

    result = translator.translate_text(text, source_lang=sourse_lang,target_lang=traget_lang)
    
    return result.text
