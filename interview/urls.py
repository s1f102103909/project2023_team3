from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('practice', views.interview_practice, name='practice'),
    path('score', views.score, name='score'),
    path('signup', views.signup, name='signup'),
]