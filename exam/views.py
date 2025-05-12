from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from account.models import CustomUser
from bot.tasks import bot
from exam.models import Level, Question, Answer
from exam.serializers import LevelSerializer, QuestionSerializer, AnswerSerializer, UserAnswerSerializer


# Create your views here.

class LevelListCreate(ListCreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get_queryset(self):
        queryset = Level.objects.all()

        search = self.request.GET.get('search')

        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class LevelDetail(RetrieveUpdateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer


class QuestionListCreate(ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.all()

        search = self.request.GET.get('search')
        level = self.request.GET.get('level')

        if search:
            queryset = queryset.filter(name__icontains=search)

        if level:
            queryset = queryset.filter(level__id=level)
        return queryset


class QuestionDetail(RetrieveUpdateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class QuestionsCheck(APIView):
    @swagger_auto_schema(
        request_body=UserAnswerSerializer(many=True),
        operation_description="Check answers and calculate score.",
        responses={
            200: openapi.Response(
                description="Result summary",
                examples={
                    "application/json": {
                        "correct": 0,
                        "incorrect": 0,
                        "total": 0,
                        "ball": "0/100"
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        answers = request.data

        if not isinstance(answers, list):
            return Response({"error": "Expected a list of answers"}, status=status.HTTP_400_BAD_REQUEST)

        total = len(answers)
        correct = 0
        incorrect = 0

        for item in answers:
            question_id = item.get("question_id")
            answer_id = item.get("answer_id")

            if not question_id or not answer_id:
                incorrect += 1
                continue

            try:
                answer = Answer.objects.get(id=answer_id, question_id=question_id)
                if answer.is_correct:
                    correct += 1
                else:
                    incorrect += 1
            except Answer.DoesNotExist:
                incorrect += 1

        ball = round((correct / total) * 100) if total > 0 else 0

        user = CustomUser.objects.filter(role="Admin").all()
        text = """
        "correct": correct,
        "incorrect": incorrect,
        "total": total,
        "ball": f"{ball}/100"
        """
        bot.send_message(chat_id=user.chat_id,text=text)

        return Response({
            "correct": correct,
            "incorrect": incorrect,
            "total": total,
            "ball": f"{ball}/100"
        })



class AnswerListCreate(ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

    def get_queryset(self):
        queryset = Answer.objects.all()

        search = self.request.GET.get('search')
        is_correct = self.request.GET.get('is_correct')
        question = self.request.GET.get('question')

        if search:
            queryset = queryset.filter(name__icontains=search)

        if is_correct:
            queryset = queryset.filter(is_correct=is_correct.capitalize())

        if question:
            queryset = queryset.filter(question__id=question)

        return queryset


class AnswerDetail(RetrieveUpdateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer

