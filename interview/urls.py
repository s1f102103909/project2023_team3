from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practice/', views.practice, name='practice'),
    #path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('process_text/',views.process_text,name='process'),
    path('check_speech_end/', views.check_speech_end, name='check_speech_end'),
    path('practice1/',views.interview_practice,name='practice1'),
]