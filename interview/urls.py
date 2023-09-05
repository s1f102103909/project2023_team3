from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    #path('transcribe/', views.transcribe_audio, name='transcribe_audio'),
    path('process_text',views.process_text,name='process_text'),
]