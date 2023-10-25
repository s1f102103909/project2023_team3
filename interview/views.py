from django.shortcuts import render
from django.http import HttpResponse, StreamingHttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
import cv2
from django.views import View
from django.views.decorators import gzip
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt

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
        'chat_results' : chat_results,
    }
    return HttpResponse(template.render(context, request))

# ストリーミング画像・映像を表示するview
#@require_GET
#class IndexView(View):
    #def get(self, request):
        #return render(request, "practice.html", {})

# ストリーミング画像を定期的に返却するview
@gzip.gzip_page
#@require_POST
def camera_stream(request):
    #if request.method == "POST":
        return StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

# フレーム生成・返却する処理
def generate_frame():
    capture = cv2.VideoCapture(0)

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