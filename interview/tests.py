from django.test import TestCase

# Create your tests here.
import os
import openai
import cv2
from django.http import StreamingHttpResponse
from django.views import View

API_KEY = "7mEzWE1lX1ydPML-R6XoIyHY3COyv4opLtNNdKTvrGfOcfITVbSVovOVaRpKORvGcl4OTip5DQweV_BAzK3L9dw"
API_BASE = "https://api.openai.iniad.org/api/v1"

def generate_answer(prompt):
    openai.api_key = API_KEY
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