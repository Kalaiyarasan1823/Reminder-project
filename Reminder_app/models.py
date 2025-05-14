from django.db import models
from django.contrib.auth.models import User
from datetime import date
from datetime import time

class Reminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField(default=date.today)  
    time = models.TimeField(default=time(12, 0))
   
    def __str__(self):
        return self.title
