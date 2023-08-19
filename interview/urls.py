from django.urls import path
from . import views
from .views import CameraView
from .views import CameraStreamView

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('get_frame/', CameraView.as_view(), name='get_frame'),
    path('capture_camera/', CameraStreamView.as_view(), name='capture_camera'),
    path('stream/', CameraStreamView.as_view(stream=True), name='camera_stream'),
]