from django.shortcuts import render
from django.http import HttpResponse
from .forms import ChatForm
from django.template import loader
from .tests import generate_answer
import cv2

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
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return HttpResponse("Failed to open the camera.")

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter('output.mp4', fourcc, fps, (w, h))

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        cv2.imshow('camera', frame)
        out.write(frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    return HttpResponse("Recording completed")



def display_video(request):
    video_path = 'output.mp4'  # output.avi の実際のパスに置き換えてください
    context = {'video_path': video_path}
    return render(request, 'video_display.html', context)