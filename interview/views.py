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
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
from .tests import text_to_speech
from .models import UserInformation


#api key
openai.api_key = '234beG84Ybh7BeumEJr6kfmjPSulkprNO9a_BRS89Ai922HJmqVkS7RYt29B3r_YtvnTcegVG7Jczx06iQ6cHzw'
openai.api_base = 'https://api,openai.iniad.org/api/v1'

SoundFile_Path = "/soundfile/file.wav"
# Create your views here.

def home(request):
    return render(request, 'interview/home.html', {}) 

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
        text_to_speech(res)
        chat_results = response
            
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))

def score(request):
    user = UserInformation.objects.get(Name=request.user.id)
    context = {
        "max_score" : user.Shushoku_maxScore,
        "previous_score" : user.Shushoku_previousScore
    }
    return render(request, 'interview/score.html', context) 

