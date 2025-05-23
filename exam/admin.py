from django.contrib import admin

from exam.models import Question, Answer


# # Register your models here.
# @admin.register(Answer)
# class AnswerAdmin(admin.ModelAdmin):
#     list_display = ["question__name","name","is_correct"]
#     list_filter = ["is_correct"]
#     search_fields = ["question__name"]
