from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
import cv2
import threading
from django.views import View
from django.http import StreamingHttpResponse
from django.template.response import TemplateResponse

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
                ・企業の入社面接を想定しください。
                ・質問を1つずつしてください
                ・私の回答に1つ1つに、採点を行なってください。
                 """
        response = generate_answer(prompt)
        chat_results = response
            
    else:
        form = ChatForm()
    template = loader.get_template('interview/practice.html')
    context = {
        'form' : form, 
        'chat_results' : chat_results
    }
    return HttpResponse(template.render(context, request))

class CameraStreamView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.video_capture = cv2.VideoCapture(0)  # 0は内蔵カメラを示します

    def __del__(self):
        self.video_capture.release()

    def get_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            _, jpeg_frame = cv2.imencode('.jpg', frame)
            return jpeg_frame.tobytes()
        return None

    def get(self, request, *args, **kwargs):
        return TemplateResponse(request, 'camerastream/practice.html')

    def stream(self, request, *args, **kwargs):
        return StreamingHttpResponse(self.stream_generator(), content_type="multipart/x-mixed-replace;boundary=frame")

    def stream_generator(self):
        while True:
            frame = self.get_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

class CameraView(View):
    def get(self, request):
        # カメラの初期化
        cap = cv2.VideoCapture(0)  # 内部カメラにアクセスする場合、0を指定
        if not cap.isOpened():
            return StreamingHttpResponse("Cannot access camera")

        def generate_frames():
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            cap.release()

        return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')