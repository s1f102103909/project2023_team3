from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.

class UserInformation(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    shushoku_previousScore = models.IntegerField(blank=True)
    shushoku_maxScore = models.IntegerField(blank=True)
    

    def __str__(self):
        return str(self.name)

def user_created(sender, instance, created, **kwargs):
    if created:
        user_obj = UserInformation(name = instance)
        user_obj.shushoku_previousScore = 0
        user_obj.shushoku_maxScore = 0
        user_obj.save()

post_save.connect(user_created, sender=User)