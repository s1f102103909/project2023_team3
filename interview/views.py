
from django.shortcuts import render
import openai
import pyaudio
import wave
import numpy as np
import time
import audioop
import gtts
from playsound import playsound
from io import BytesIO
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
from .models import UserInformation
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
#api key
openai.api_key = '234beG84Ybh7BeumEJr6kfmjPSulkprNO9a_BRS89Ai922HJmqVkS7RYt29B3r_YtvnTcegVG7Jczx06iQ6cHzw'
openai.api_base = 'https://api,openai.iniad.org/api/v1'
SoundFile_Path = "/soundfile/file.wav"
from .tests import speech_active
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import speech_recognition as sr
from pydub import AudioSegment
import io
from .tests import Voicevox

# Create your views here.

def home(request):
    return render(request, 'interview/home.html', {}) 

@csrf_exempt
def interview_practice(request):
    chat_results = ""
    if request.method == "POST":
        # ChatGPTボタン押下時
        form = ChatForm(request.POST)
        #if form.is_valid():
        #prompt = form.cleaned_data['prompt']
        prompt = """
                今から面接を始めます。あなたは面接官で、私が受験者です。以下の条件に従って、面接を行なってください。
                ・IT企業の入社面接を想定しください。
                ・質問を1つずつしてください
                ・私の回答に1つ1つに、採点を行なってください。
                 """
        response = generate_answer(prompt)
        res = response.replace('面接官:', '')
        chat_results = res

<<<<<<< Updated upstream
            
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))
import json
=======
def start(request):
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

    waveFile = wave.open(SoundFile_Path, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(iAudio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def speech_to_text(filepath):

    # ファイルを開く
    audio_file= open(filepath, "rb")

    # Speech to Text変換
    response = openai.Audio.transcribe(model = "whisper-1", # Speech-to-Textモデル
                                       file  = audio_file,  # オーディオファイル
                                      )
    
    # 変換後のテキスト出力
    return response.text
>>>>>>> Stashed changes


def score(request):
    user = UserInformation.objects.get(Name=request.user.id)
    context = {
        "max_score" : user.Shushoku_maxScore,
        "previous_score" : user.Shushoku_previousScore
    }
    return render(request, 'interview/score.html', context) 

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, "interview/signup.html", {"form":form})

def check_speech_end(request):
    return JsonResponse({'active':recognition.is_listening()})

@csrf_exempt
def process_text(request):
    if request.method == 'POST':
        #text = request.POST.get('text')
        # テキストの処理を実行
        # ...
        # 応答を返す

        # 処理されたテキストをセッションに保存
        #request.session['processed_text'] = text
        
        #return JsonResponse({'message': text })
    #else:
        #return JsonResponse({'message': 'Invalid request method'})
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        text = body_data['text']
        response = generate_answer(text)

        return JsonResponse({'message': response})
