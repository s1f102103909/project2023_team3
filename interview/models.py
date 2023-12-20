from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import datetime
import os

# Create your models here.

def dir_path_name(instance, filename):
    date_time = datetime.datetime.now() # 現在の時刻を取得
    date_dir = date_time.strftime('%Y年/%m月/%d日') # 年/月/日のフォーマット作成
    time_stamp = date_time.strftime('%H時%M分.mp4') #時分のフォーマットの作成
    dir_path = os.path.join('video', date_dir, time_stamp)
    return dir_path

class UserInformation(models.Model):
    Name = models.OneToOneField(User, on_delete=models.CASCADE, null=False)
    advise = models.CharField(max_length=1000, null=True, blank=True)
    video = models.FileField(upload_to=dir_path_name, null=True, blank=True)
    
    def __str__(self):
        return str(self.Name)
    

def user_created(sender, instance, created, **kwargs):
    if created:
        user_obj = UserInformation(Name = instance)
        user_obj.advise = ""
        user_obj.save()

post_save.connect(user_created, sender=User)