
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
                今から面接を始めます。以下の条件に従って、面接を行なってください。
                ・あなたは面接官で、私は面接者です。
                ・IT企業の入社面接を想定しください。
                ・質問を1つずつしてください。
                ・私の回答に1つ1つに、採点を行なってください。
                ・採点は面接終了時にしてください。
                ・自問自答しないでください。
                 """
        response = langchain_GPT(prompt)
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
        response = langchain_GPT(text)

        return JsonResponse({'message': response})
