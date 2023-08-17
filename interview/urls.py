from django.urls import path
from . import views
from .views import CameraView
from .views import get_frame

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('camera/', views.CameraView.as_view(), name='camera_view'),  # 新しいパスを追加
    path('get_frame/', views.get_frame, name='get_frame'),          # 新しいパスを追加
]