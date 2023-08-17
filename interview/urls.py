from django.urls import path
from . import views
from .views import CameraView
from .views import get_frame

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('practice/', CameraView.as_view(), name='practice_view'),
    path('get_frame/', get_frame, name='get_frame'),
]