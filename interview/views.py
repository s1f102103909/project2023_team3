from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
import cv2
import threading
from django.views import View
from django.http import StreamingHttpResponse

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
    display_camera()

class CameraView(View):
    template_name = 'practice.html'

    def get(self, request, *args, **kwargs):
        template = loader.get_template(self.template_name)
        return HttpResponse(template.render({}, request))

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.frame = None
        self.is_running = True

    def start(self):
        thread = threading.Thread(target=self._capture_frames)
        thread.start()

    def stop(self):
        self.is_running = False
        self.video.release()

    def _capture_frames(self):
        while self.is_running:
            ret, frame = self.video.read()
            if not ret:
                break
            self.frame = frame

    def get_frame(self):
        return self.frame

camera = VideoCamera()
camera.start()

def get_frame(request):
    def generate():
        while True:
            frame = camera.get_frame()
            if frame is not None:
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    return StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')