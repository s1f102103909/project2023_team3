from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('accounts/login/', views.Login, name="login"),
    path('score', views.score, name='score'),
    path('signup', views.signup, name='signup'),
    #path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('process_text/',views.process_text,name='process'),
    path('camera_stream', views.camera_stream, name='camera_stream'),
    path('result', views.result, name='result'),
    path('error', views.error, name="error"),
]