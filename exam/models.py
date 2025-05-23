from django.db import models

from command.models import BaseModel


# Create your models here.
class Level(BaseModel):
    name = models.CharField(max_length=100)
    time = models.CharField(max_length=100,null=True, blank=True)
    def __str__(self):
        return self.name


class Question(BaseModel):
    name = models.TextField()
    level : "Level" = models.ForeignKey("exam.Level", on_delete=models.CASCADE, related_name="questions_level")
    def __str__(self):
        return self.name


class Answer(BaseModel):
    question : "Question" = models.ForeignKey("exam.Question", on_delete=models.CASCADE, related_name="answers_question")

    name = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)
    def __str__(self):
        return self.question.name

