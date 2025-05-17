from django.db import models

from command.models import BaseModel
from exam.models import Level,Question,Answer

from account.models import CustomUser

# Create your models here.

class Result(BaseModel):
    level : "Level" = models.ForeignKey("exam.Level",on_delete=models.SET_NULL,null=True,blank=True)
    user : "CustomUser" = models.ForeignKey("account.CustomUser",on_delete=models.CASCADE)

    correct_answer = models.CharField("Correct Answer",max_length=100, null=True, blank=True)
    ball = models.CharField("Ball",max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username




