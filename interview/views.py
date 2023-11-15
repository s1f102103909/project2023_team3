
from django.shortcuts import render
import openai
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import langchain_GPT
from .models import UserInformation
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
import os
#api key
openai.api_key = os.environ.get('OPENAI_API_KEY')
openai.api_base = 'https://api,openai.iniad.org/api/v1'
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
# Create your views here.

from .tests import JP_To_EN
from .tests import EN_To_JP

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
                You are an interviewer for an IT company. I am the interviewer. I am about to start interviewing new graduates. Please observe the following rules during the interview.
                    1.the behavior of the interviewer
                    2.To greet the interviewer briefly at the beginning.
                    3.Ask the next question in response to my reply.
                    4.To ask questions based on my replies.
                    5.Do not reply to your own questions.
                    6.Listen carefully to the candidate's answers and ask follow-up questions.
                    7.Speak in the interviewee's speaking style.
                    8.Do not ask myself questions.
                Now please begin the interview.
                 """
        response = langchain_GPT(prompt)
        #res = response.replace('面接官:', '')
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
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        text = body_data['text']
        en_text = JP_To_EN(text)
        response = langchain_GPT(en_text)
        jp_response = EN_To_JP(response)

        return JsonResponse({'message': jp_response})
    

def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audioFile'):
        audio_file = request.FILES['audioFile']
        url = "https://ai-api.userlocal.jp/voice-emotion/basic-emotions"
    with open(''.format(audio_file), 'rb') as voice:
        response = requests.post(url, files={"voice_data": voice})
        result = json.loads(response.content)
    for emotion in result['emotion_detail'].keys():
        if "neutral" in emotion:
            if 'values' not in request.session:
               request.session['values'] = []
            request.session['values'].append(f"{emotion}: {result['emotion_detail'][emotion]}")
    
def emotion(request,x):
    url = "https://ai-api.userlocal.jp/voice-emotion/basic-emotions"
    with open('../project2023_team3/voice({:>3}).mp3'.format(x), 'rb') as voice:
        response = requests.post(url, files={"voice_data": voice})
        result = json.loads(response.content)
    for emotion in result['emotion_detail'].keys():
        if "neutral" in emotion:
            if 'values' not in request.session:
               request.session['values'] = []
            request.session['values'].append(f"{emotion}: {result['emotion_detail'][emotion]}")

def calculate_average(request):
    values = request.session.get('values', [])
    if values:
        average = sum(values) / len(values)
        return JsonResponse({'average': average})
    else:
        return JsonResponse({'error': 'No values available for calculation'})