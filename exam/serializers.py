from rest_framework import serializers

from exam.models import Level, Question, Answer


class LevelSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = [
            "id",
            "name",
            "time",
            "question",
            "created_at",
            "updated_at"
        ]

    def get_question(self, obj):
        questions = Question.objects.filter(level=obj)
        return QuestionSerializer(questions, many=True).data


class QuestionSerializer(serializers.ModelSerializer):
    answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "name",
            "answer",
            "level",
        ]

    def get_answer(self, obj):
        answers = Answer.objects.filter(question=obj)
        return AnswerSerializer(answers, many=True).data


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = [
            "id",
            "question",
            "name",
            "is_correct",
        ]

class UserAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()