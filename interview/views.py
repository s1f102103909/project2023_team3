from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
import cv2
import os
from django.views import View
from django.conf import settings
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


class CameraView(View):
    def get(self, request):
        def generate_frames():
            cap = cv2.VideoCapture(0)  # 内部カメラにアクセスする場合、0を指定
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            media_root = settings.MEDIA_ROOT
            output_path = os.path.join(media_root, 'output.avi')
            out = cv2.VideoWriter(output_path, fourcc, 20.0, (640, 480))

            if not cap.isOpened():
                yield b'Cannot access camera'

            while True:
                ret, frame = cap.read()
                out.write(frame)
                if not ret:
                    break

                ret, buffer = cv2.imencode('.jpg', frame)
                if ret:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

            # 映像を保存
            cap.release()
            try:
                out.release()
            except Exception as e:
                print("Error releasing VideoWriter:", e)
            cv2.destroyAllWindows()

        return StreamingHttpResponse(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def display_video(request):
    video_path = '/path/to/output.avi'  # output.avi の実際のパスに置き換えてください
    context = {'video_path': video_path}
    return render(request, 'video_display.html', context)