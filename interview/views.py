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
import requests 
import json 
import os

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

            
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))
import json


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

######変更部分＃＃＃＃＃
 

def emotion(request,x):
    url = "https://ai-api.userlocal.jp/voice-emotion/basic-emotions"
    #emotion_result = []
    with open('../project2023_team3/voice({:>3}).mp3'.format(x), 'rb') as voice:
        response = requests.post(url, files={"voice_data": voice}) 
        result = json.loads(response.content)
    for emotion in result['emotion_detail'].keys(): 
        if "neutral" in emotion:
            if 'values' not in request.session:
               request.session['values'] = []
            request.session['values'].append(f"{emotion}: {result['emotion_detail'][emotion]}")
            #emotion_result.append(f"{emotion}: {result['emotion_detail'][emotion]}")
    

def calculate_average(request):
    values = request.session.get('values', [])
    if values:
        average = sum(values) / len(values)
        return JsonResponse({'average': average})
    else:
        return JsonResponse({'error': 'No values available for calculation'})









#def emotion_fin(request):
    #n = 0
    #mid_result = 0
    #dir = '../project2023_team3'
    

    #for i in range(0,sum(os.path.isfile(os.path.join(dir, name)) for name in os.listdir(dir))+1):
        #n += 1
        #x = emotion(request,i)
        #mid_result += x
    #result = mid_result/n
    #return JsonResponse({'result': result})
