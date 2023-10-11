from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
import cv2
import moviepy.editor as mp
import datetime
import time

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

def interview_recording(request):
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"output{formatted_datetime}.mp4"
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return HttpResponse("Failed to open the camera.")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (w, h))
    start_time = time.time()
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow('camera', frame)
        out.write(frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == ord(' '):
            break
        current_time = time.time()
        if cv2.waitKey(1) & 0xFF == ord('q') or (current_time - start_time) >= 30:
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return HttpResponse("録画を保存しました")

