from django.shortcuts import render, redirect
from django.http import StreamingHttpResponse
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
import openai
from pydub import AudioSegment
import time
import requests
import glob, shutil
import matplotlib.pyplot as plt
import re
import alkana

# Create your views here.
# global変数
API_KEY_INIAD ="ehoIeOxmC5m1SAEwGLysEqLy5QIh0XwWLp3zIlBAcy4dcsi2BhH_L_fo8lQVK27HxijRfbqqEHgqeWTOiReCwIQ"
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

speechTexts = [] # 音声合成したテキストを格納する変数
responseTexts = [] # 返答テキストを格納する変数

start_time = 0.0    #録音開始時刻の初期設定
user_end_time = []  #ユーザーの喋り終わりの時間の配列
voicebox_end_time = []  #VoiceBoxの喋り終わりの時間の配列

audio_dir = "cutaudio"

#home.htmlへの遷移
def home(request):
    return render(request, 'interview/home.html', {}) 

#練習開始ボタンを押した時の挙動
@csrf_exempt
def interview_practice(request):
    global chatgpt_chain, rec_flag, start_time
    rec_flag = False
    start_recording_thread = threading.Thread(target=rec2_start)
    if request.method == "GET":
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
        return render(request, "interview/practice.html", {})

    if request.method == 'POST':
        #撮影してないならば、撮影スタート
        if rec_flag == False:
            start_recording_thread.start()
            start_time = time.time()    #撮影開始時刻
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
        responseTexts.append("面接官:{0}".format(response))
    
        return JsonResponse({'message': response})

#ホーム画面から成績画面の遷移
def score(request):
    user = UserInformation.objects.get(Name=request.user.id)
    context = {
        "advise" : user.advise,
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

@csrf_exempt
def process_text(request):
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        body_data = json.loads(body_unicode)
        text = body_data['text']
        user_end_time.append(time.time())
        speechTexts.append("あなた:{0}".format(text))
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
        sound_cut()
        rec_flag = False

        interview_result = ChatGPT_to_Result(speechTexts,responseTexts)
        print(interview_result)
        score_point = interview_result.find("Score")
        Evaluation_point = interview_result.find("Evaluation")
        Advice_point = interview_result.find("Advice")
        Score = interview_result[score_point+6:Evaluation_point]
        Evaluation = interview_result[Evaluation_point+11:Advice_point]
        Advice = interview_result[Advice_point+23:]
        Score = EN_To_JP(Score)
        Evaluation = EN_To_JP(Evaluation)
        Advice = EN_To_JP(Advice)
        context = {'score': Score,'evaluation':Evaluation,'advice':Advice}
        user.advise = Advice
        user.save()
        with open("main.mp4", "rb") as video_file:
            user.video.save(os.path.basename("") ,File(video_file), save=True)
        return render(request, 'interview/result.html',context)
    else:
        return render(request, 'interview/result.html',{})

#何かしらエラーが発生した時に、エラー画面へ遷移
def error(request):
    return render(request, 'interview/error.html', {})

#引数に文章を渡すと、ChatGPTから返信が来る
def langchain_GPT(text):
    output = chatgpt_chain.predict(input=text)
    #output = output.replace('AI', '')
    output = EN_To_JP(output)
    responseTexts.append("面接官:{0}".format(output))
    vv = Voicevox()
    vv.speak(text=draw_english(output))
    voicebox_end_time.append(time.time())   #VoiceBoxが喋り終わった時間
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

def ChatGPT_to_Result(speechTexts,responseTexts):
    history = ""
    for i in range(len(speechTexts)):
        history += "{0}\n".format(responseTexts[i])
        history += "{0}\n".format(speechTexts[i])
    openai.api_key = API_KEY_INIAD
    openai.api_base= API_BASE
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role":"system",
             "content":"""
                    YYou are a professional interview critic. Please evaluate and advise on the interview's dialogue history.
                    Also, please grade the interview on a 100-point scale. Please be strict in your scoring.
                    Output should be in the following format
                    ------
                    Score: Evaluation Score
                    Evaluation: Evaluation details
                    Advice for improvement: Advice 
                    ------
                    """},
            {"role":"user",
             "content":history}
        ]
    )
    return response.choices[0]['message']['content']

#ユーザーの音声だけを抜き取る
def sound_cut():
    global start_time, user_end_time, voicebox_end_time
    if os.path.isdir(audio_dir):
        shutil.rmtree(audio_dir)
    os.makedirs("cutaudio")
    for i in range(len(user_end_time)):
        diff_with_voicebox = voicebox_end_time[i] - start_time
        diff_with_user = user_end_time[i] -start_time
        sound = AudioSegment.from_file("output_audio.wav", format="wav")
        cutsound = sound[diff_with_voicebox*1000:diff_with_user*1000]
        cutsound.export(f"cutaudio/score{i+1}.wav", format="wav")

#ユーザーの音声から、感情を判定
def voice_result():
    angry = []
    disgust = []
    fear = []
    happy = []
    neutral = []
    sad = []
    suprise = []
    emotion_dic = {"angry":angry, "disgust":disgust, "fear":fear, "happy":happy, "neutral":neutral, "sad":sad, "suprise":suprise}
    file_pat = "{}/*.wav".format(audio_dir)
    url = "https://ai-api.userlocal.jp/voice-emotion/basic-emotions"
    for file_path in glob.glob(file_pat):
        with open(file_path, 'rb') as voice:
            response = requests.post(url, files={"voice_data":voice})
            result = json.loads(response.content)
            if result["status"] != "error":
                for emotion in result["emotion_detail"].keys():
                    #print(f"{emotion}: {result['emotion_detail'][emotion]}")
                    emotion_dic[emotion].append(result["emotion_detail"][emotion])

    graph(emotion_dic)

def graph(emotion_dic):
    x = list(range(1, len(next(iter(emotion_dic.values()))) + 1))
    plt.figure(figsize=(10, 6))
    
    for emotion, values in emotion_dic.items():
       marker_styles = {
           "angry": 'o',      # 丸
           "disgust": 's',    # 四角
           "fear": '^',       # 上向き三角
           "happy": '*',      # 星
           "neutral": 'x',    # バツ
           "sad": 'D',        # ダイヤ
           "surprise": 'P'    # 五角形
       }
    
       # カラーのマッピングも追加
       color_styles = {
           "angry": 'r',
           "disgust": 'c',
           "fear": 'k',
           "happy": 'm',
           "neutral": 'g',
           "sad": 'b',
           "surprise": 'y'
       }
    
       plt.plot(x, values, label=emotion.capitalize(), marker=marker_styles[emotion], color=color_styles[emotion])
    
    #plt.xlabel('Time')  # x軸のラベル
    #plt.ylabel('Emotion Intensity')  # y軸のラベル
    plt.legend()  # 凡例の表示
    plt.grid(True)  # グリッドの表示
    
    plt.tight_layout()  # レイアウトの調整
    plt.savefig("emotion_graph.png")
def draw_english(text):
    english_list = re.findall(r"[A-Za-z]+",text)
    japanese_list = []
    for english in english_list:
        japanese_list.append(alkana.get_kana(english))
    for i in range(len(english_list)):
        text.replace(english_list[i],japanese_list[i])
    return text
