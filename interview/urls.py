from django.urls import path
from . import views
#from .views import CameraView

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('capture_and_save', views.capture_and_save, name='capture_and_save'),
]