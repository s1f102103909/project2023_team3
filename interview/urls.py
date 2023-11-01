from django.urls import path
from . import views
#from .views import CameraView

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('camera_stream', views.camera_stream, name='camera_stream'),
]