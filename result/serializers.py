from rest_framework import serializers

from exam.models import Level
from exam.serializers import LevelSerializer
from result.models import Result


class ResultsSerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    class Meta:
        model = Result
        fields = [
            "id",
            "level",
            "user",
            "correct_answer",
            "ball",
            "created_at"
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["level"] = LevelSerializer(instance.level).data
        return rep