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

#api key
openai.api_key = '234beG84Ybh7BeumEJr6kfmjPSulkprNO9a_BRS89Ai922HJmqVkS7RYt29B3r_YtvnTcegVG7Jczx06iQ6cHzw'
openai.api_base = 'https://api,openai.iniad.org/api/v1'

SoundFile_Path = "/soundfile/file.wav"
# Create your views here.

def home(request):
    return render(request, 'interview/home.html', {}) 


def start():
    # ボタンを押すなどのイベントがない場合は一定時間後に自動で録音を開始
    N = 5  # 無音検出時間（秒）
    THRESHOLD = 2000  # 音量のしきい値

    # 音声録音関係のパラメータ
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 2**11
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "file.wav"

    iAudio = pyaudio.PyAudio()

    # 録音開始
    stream = iAudio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        rms = audioop.rms(data, 2)  # 音量の取得
        if rms < THRESHOLD:  # 音量がしきい値を下回ったらカウント開始
            time.sleep(N)
            rms = audioop.rms(stream.read(CHUNK), 2)
            if rms < THRESHOLD:  # N秒後もしきい値を下回っていたら録音終了
                break

    # 録音終了
    stream.stop_stream()
    stream.close()
    iAudio.terminate()

    waveFile = wave.open(SoundFile_Path, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(iAudio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def speech_to_text(filepath):

    # ファイルを開く
    audio_file= open(filepath, "rb")

    # Speech to Text変換
    response = openai.Audio.transcribe(model = "whisper-1", # Speech-to-Textモデル
                                       file  = audio_file,  # オーディオファイル
                                      )
    
    # 変換後のテキスト出力
    return response.text


def text_to_speech():
    # file を保存してから音声を流す

    # text入力 -> tts(音声ファイル)
    tts = gtts.gTTS("hello world",lang="en") # Janpanese : ja;
    # 音声ファイル保存
    tts.save("/soundfile/hello.mp3")
    # play
    playsound("/soundfile/hello.mp3")

    # 音声を直接流す
    mp3_fp = BytesIO()
    tts = gtts.gTTS("hello world",lang="en")
    tts.write_to_fp(mp3_fp)