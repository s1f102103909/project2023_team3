from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from .forms import ChatForm
from django.template import loader
from .models import UserInformation
from .forms import SignUpForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators import gzip
import cv2
import threading
import moviepy.editor as mp
from langchain.llms.openai import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferWindowMemory
from .tests import Voicevox
import subprocess

# Create your views here.
# global変数
API_KEY_INIAD = "7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw"
API_BASE = "https://api.openai.iniad.org/api/v1"

fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 動画コーデックの設定（XVIDは一般的なコーデック）
video_filename = 'output.mp4'
fps = 0.0
width = 0
height = 0
out = cv2.VideoWriter()

audio_filename = 'output_audio.mp3'
rec_flag = False


def langchain_GPT(text):
    output = chatgpt_chain.predict(input=text)
    output = output.replace('面接官', '')
    vv = Voicevox()
    vv.speak(text=output)
    return output

def home(request):
    return render(request, 'interview/home.html', {}) 

@csrf_exempt
def interview_practice(request):
    global chatgpt_chain, rec_flag
    rec_flag = False
    chat_results = ""
    start_recording_thread = threading.Thread(target=start_recording)

    template = """
            {history}
            Human: {input}
            AI: 
            """
    prompt = PromptTemplate(
        input_variables = ["history","input"],
        template = template
    )   
    chatgpt_chain = LLMChain(
        llm = OpenAI(temperature=0, openai_api_key=API_KEY_INIAD, openai_api_base=API_BASE),
        prompt=prompt,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=10, memory_key="history"),
    )

    if request.method == "POST":
        # ChatGPTボタン押下時
        form = ChatForm(request.POST)
        start_recording_thread.start()
        prompt = """
        あなたには今から新卒面接の面接官役になってもらいこちらの面接の練習をしてもらいます。以下を気を付けてください。
            ・最初は名前と学校名を聞いてください
            ・IT企業の面接ということを意識しながら質問をしてください
            ・質問は1会話に1つずつお願いします
        ではお願いします
        """
        response = langchain_GPT(prompt)
        res = response.replace('面接官', '')
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
    
# ストリーミング画像を定期的に返却するview
@gzip.gzip_page
def camera_stream(request):
    return StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

# フレーム生成・返却する処理
def generate_frame():
    global frame, width, height, fps, out
    capture = cv2.VideoCapture(0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    capture.set(cv2.CAP_PROP_FPS, 30)
    fps = capture.get(cv2.CAP_PROP_FPS)

    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        # カメラからフレーム画像を取得
        ret, frame = capture.read()

        if not ret:
            print("Failed to read frame.")
            break
        # フレーム画像バイナリに変換
        ret, jpeg = cv2.imencode('.jpg', frame)
        byte_frame = jpeg.tobytes()

        # フレーム画像のバイナリデータをユーザーに送付する
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')

        # フレームを動画ファイルに書き込む 
        out.write(frame)

def result(request):
    rec_stop()
    return render(request, 'interview/result.html', {}) 

def start_recording():
    global out, width, height, fps

    # ファイル名、コーデック、フレームレート、フレームサイズを設定
    out = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))
    rec_start()

def rec_start():
    global p, rec_flag
    if rec_flag == False:
        cmd = "rec -q output_audio.mp3"
        p = subprocess.Popen(cmd.split())
        rec_flag = True
    print("OK")
    return None

def rec_stop():
    global p, rec_flag
    if rec_flag == True:
        p.terminate()
        try:
            p.wait(timeout=1)
            rec_flag = False
        except subprocess.TimeoutExpired:
            p.kill()
            rec_flag = False
    print("OK")
    out.release()
    video = mp.VideoFileClip(video_filename)
    video = video.set_audio(mp.AudioFileClip(audio_filename))
    video.write_videofile("main.mp4")
    return None

        