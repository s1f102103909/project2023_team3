from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
#from .tests import generate_answer
from .tests import langchain_GPT
from langchain.llms.openai import OpenAI 
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

# Create your views here.
def home(request):
    return render(request, 'interview/home.html', {}) 

def interview_practice(request):
    chat_results = ""

    if request.method == "POST":
        # ChatGPTボタン押下時
        form = ChatForm(request.POST)
        if form.is_valid():
            prompt = form.cleaned_data['prompt']
            #print(type(prompt))
            response = langchain_GPT(prompt)
            chat_results = response
            
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))


