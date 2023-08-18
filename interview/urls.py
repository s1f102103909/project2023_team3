from django.urls import path
from . import views
from .views import CameraView

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('get_frame/', CameraView.as_view(), name='get_frame'),
]