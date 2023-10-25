from django.test import TestCase

# Create your tests here.
import os
import openai 
from langchain.llms.openai import OpenAI 
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory

API_KEY_INIAD = "7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw"
#API_KEY = "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"
API_BASE = "https://api.openai.iniad.org/api/v1"

#openai.api_key = API_KEY_INIAD
#openai.api_key = API_KEY
#openai.api_base = API_BASE
#openai.Model.list() #OpenAIのインスタンスを生成

#OpenAI.openai_api_key = API_KEY_INIAD
#OpenAI.openai_api_key = API_KEY
#OpenAI.openai_api_base = API_BASE
    
    
template = """
            {history}
            面接者: {input}
            AI:""
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
    return output
'''
def generate_answer(prompt):

    openai.api_key = API_KEY_INIAD
    #openai.api_key = API_KEY
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
'''