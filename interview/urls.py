from django.urls import path
from . import views
#from .views import CameraView

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    #path('practice', views.IndexView.as_view()),
    #path('recording', views.interview_recording, name='recording'),
    #path('display_video', views.display_video, name='display_video'),
    path('camera_stream', views.camera_stream, name='camera_stream'),
]