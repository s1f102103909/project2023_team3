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
from .tests import EN_To_JP, JP_To_EN
import pyaudio
import wave
from django.core.files import File
import os

# Create your views here.
# global変数
API_KEY_INIAD =os.environ.get('7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw')
API_BASE = "https://api.openai.iniad.org/api/v1"
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 動画コーデックの設定（XVIDは一般的なコーデック）
video_filename = 'output.mp4'             #動画ファイル名(音無し)
fps = 0.0                                 #fpsの初期設定
width = 0                                 #カメラの幅
height = 0                                #カメラの縦
out = cv2.VideoWriter()                   #フレームを書き込む変数の初期化
audio_filename = 'output_audio.wav'       #音声ファイル名
rec_sig = []                              #音声フレームを格納する変数
rec_flag = False                          #撮影中かどうか

#home.htmlへの遷移
def home(request):
    return render(request, 'interview/home.html', {}) 

#練習開始ボタンを押した時の挙動
@csrf_exempt
def interview_practice(request):
    global chatgpt_chain, rec_flag
    rec_flag = False
    chat_results = ""
    start_recording_thread = threading.Thread(target=rec2_start)

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
        #撮影してないならば、撮影スタート
        if rec_flag == False:
            start_recording_thread.start()
            rec_flag = True
        #ChatGPTに面接のお願いをする文章
        prompt = """
                We will now be conducting interviews. Please follow the conditions below.
                1. You will be the interviewer and I will be the interviewee.
                2. Please assume that the interview is for a new hire at an IT company.
                3. Please ask me those questions one at a time.
                4. At the end of the interview, please signal the end of the interview and grade the interview.
                """
        #返信をresoponseへ格納
        response = langchain_GPT(prompt)
        #response = response.replace('AI', '')
        chat_results = response
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))

#ホーム画面から成績画面の遷移
def score(request):
    user = UserInformation.objects.get(Name=request.user.id)
    context = {
        "max_score" : user.Shushoku_maxScore,
        "previous_score" : user.Shushoku_previousScore,
        "video" : user.video
    }
    return render(request, 'interview/score.html', context) 

#新規登録の画面
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
        response = langchain_GPT(JP_To_EN(text))

        return JsonResponse({'message': response})
    
# ストリーミング画像を定期的に返却するview
@gzip.gzip_page
def camera_stream(request):
    return StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

#面接が終了し、結果画面への遷移
def result(request):
    global rec_flag
    user = UserInformation.objects.get(Name=request.user.id)
    if rec_flag == True:
        rec2_stop()
        rec_flag = False

        with open("main.mp4", "rb") as video_file:
            user.video.save(os.path.basename("") ,File(video_file), save=True)
        return render(request, 'interview/result.html', {}) 
    return error(request)

#何かしらエラーが発生した時に、エラー画面へ遷移
def error(request):
    return render(request, 'interview/error.html', {})

#引数に文章を渡すと、ChatGPTから返信が来る
def langchain_GPT(text):
    output = chatgpt_chain.predict(input=text)
    #output = output.replace('AI', '')
    output = EN_To_JP(output)
    vv = Voicevox()
    vv.speak(text=output)
    return output

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

#録画録音開始
def rec2_start():
    global stream, rec_sig, out, width, height, fps

    # ファイル名、コーデック、フレームレート、フレームサイズを設定
    out = cv2.VideoWriter(video_filename, fourcc, fps, (width, height))

    rec_sig = []
    p = pyaudio.PyAudio()
    stream = p.open(
        rate=44100,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=1024,
        input_device_index=0,
        stream_callback=callback,
    )
    stream.start_stream()
    print("recording now...")
    return 0

def callback(in_data, frame_count, time_info, status_flags):
    global rec_sig
    rec_sig.append(in_data)
    return None, pyaudio.paContinue

#録画録音停止
def rec2_stop():
    #録音停止
    global stream, audio_filename, rec_sig
    if stream.is_active():
        stream.stop_stream()
        stream.close()
    out.release()
    wf = wave.open(audio_filename, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(44100)
    wf.writeframes(b''.join(rec_sig))
    wf.close()

    #音声ファイルと録画ファイルの合成
    video = mp.VideoFileClip(video_filename)
    video = video.set_audio(mp.AudioFileClip(audio_filename))
    video.write_videofile("main.mp4")
    return 0
