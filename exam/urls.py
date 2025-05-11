from django.urls import path

from exam.views import LevelListCreate, LevelDetail, QuestionListCreate, QuestionDetail, AnswerListCreate, AnswerDetail, \
    QuestionsCheck

urlpatterns = [
    path("level/",LevelListCreate.as_view()),
    path("level/<uuid:pk>/",LevelDetail.as_view()),

    path("question/",QuestionListCreate.as_view()),
    path("question/<uuid:pk>/",QuestionDetail.as_view()),
    path("question/check/",QuestionsCheck.as_view()),

    path("answer/",AnswerListCreate.as_view()),
    path("answer/<uuid:pk>/",AnswerDetail.as_view()),
]