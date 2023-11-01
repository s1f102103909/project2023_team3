from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('score', views.score, name='score'),
    path('signup', views.signup, name='signup'),
    #path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('process_text/',views.process_text,name='process'),
    path('check_speech_end/', views.check_speech_end, name='check_speech_end'),
    path('camera_stream', views.camera_stream, name='camera_stream'),
]