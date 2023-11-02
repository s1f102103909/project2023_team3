
from django.shortcuts import render
import openai
from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import langchain_GPT
from .models import UserInformation
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
#api key
openai.api_key = '234beG84Ybh7BeumEJr6kfmjPSulkprNO9a_BRS89Ai922HJmqVkS7RYt29B3r_YtvnTcegVG7Jczx06iQ6cHzw'
openai.api_base = 'https://api,openai.iniad.org/api/v1'
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators import gzip
import time
import cv2
import sounddevice as sd
import soundfile as sf
import threading
import sys
import moviepy.editor as mp
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
        Interviews will be held now. Please do so according to the following conditions
        1. You will be the interviewer and I will be the interviewee.
        2. Assume you are hiring a new employee for an IT company.
        3. Please ask 5 questions.
        4. At the end of the interview, signal the end and grade the interview.
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
#@require_POST
def camera_stream(request):
    #if request.method == "POST":
        return StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')



# フレーム生成・返却する処理
def generate_frame():
    capture = cv2.VideoCapture(0)
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 動画コーデックの設定（XVIDは一般的なコーデック）
    video_filename = 'output.mp4'
    out = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))  # ファイル名、コーデック、フレームレート、フレームサイズを設定

    audio_filename = 'output_audio.mp3'
    channels = 1 # ステレオ
    duration = 30

    audio_thread = threading.Thread(target=audio_capure, args=(audio_filename, channels, duration))
    audio_thread.start()


    start_time = time.time()
    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        # カメラからフレーム画像を取得
        ret, frame = capture.read()
        # フレームを動画ファイルに書き込む
        out.write(frame)

        if not ret:
            print("Failed to read frame.")
            break
        # フレーム画像バイナリに変換
        ret, jpeg = cv2.imencode('.jpg', frame)
        byte_frame = jpeg.tobytes()

        # フレーム画像のバイナリデータをユーザーに送付する
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')

        current_time = time.time()
        if (current_time - start_time) >= 30:
            break
    out.release()
    audio_thread.join()

    video = mp.VideoFileClip(video_filename)
    video = video.set_audio(mp.AudioFileClip(audio_filename))
    video.write_videofile("main.mp4")
    #user.video = 'output.mp4'
    #user.save()

def audio_capure(audio_filename, channels, duration):
    print("Recordin audio...")
    audio_data = sd.rec(int(44100*duration), 44100, channels=channels)
    sd.wait()
    sf.write(audio_filename, audio_data, 44100)
    print("Audio recording completed.")


    
