from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
from .tests import text_to_speech

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
        text_to_speech(response)
        chat_results = response
        text_to_speech(chat_results)
            
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))


