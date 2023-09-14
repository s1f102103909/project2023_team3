from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserInformation(models.Model):
    Name = models.ForeignKey(User, on_delete=models.CASCADE)
    Shushoku_previousScore = models.IntegerField(blank=True)
    Shushoku_maxScore = models.IntegerField(blank=True)
    

    def __str__(self):
        return str(self.Name)