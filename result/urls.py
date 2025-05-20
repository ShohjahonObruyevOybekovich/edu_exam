from django.urls import path

from result.views import ResultListApiView

urlpatterns = [
    path("",ResultListApiView.as_view()),
]