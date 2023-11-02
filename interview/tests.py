from django.test import TestCase

# Create your tests here.
import os
import openai
import pyaudio
import wave
import numpy as np
import time
import requests, json
import io
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

os.environ['GOOGLE_APPLICATION_CREDENTIALS']='glossy-aloe-396205-d7fdd774bdbe.json'

API_KEY_INIAD = "7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw"
API_BASE = "https://api.openai.iniad.org/api/v1"

speech_active = False
'''
def generate_answer(prompt):
    openai.api_key = API_KEY
    openai.api_base = API_BASE
    openai.Model.list() #OpenAIのインスタンスを生成
    
    global speech_active
    speech_active = True

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
    answer = response['choices'][0]['message']['content'].replace('面接官:', '')
    vv=Voicevox()
    vv.speak(text=answer)
    return answer
'''

#openai.api_key = API_KEY_INIAD
#openai.api_key = API_KEY
#openai.api_base = API_BASE
#openai.Model.list() #OpenAIのインスタンスを生成

#OpenAI.openai_api_key = API_KEY_INIAD
#OpenAI.openai_api_key = API_KEY
#OpenAI.openai_api_base = API_BASE
    
    
template = """
            {history}
            {input}
            """
prompt = PromptTemplate(
        input_variables = ["history","input"],
        template = template
)
chatgpt_chain = LLMChain(
    llm = OpenAI(temperature=0, openai_api_key=API_KEY_INIAD, openai_api_base=API_BASE),
    prompt=prompt,
    verbose=True,
    memory=ConversationBufferWindowMemory(k=10),
)

def langchain_GPT(text):
    output = chatgpt_chain.predict(input=text)
    output = output.replace('面接官', '')
    vv = Voicevox()
    vv.speak(text=output)
    return output
    
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