from rest_framework.generics import ListAPIView

from result.models import Result
from result.serializers import ResultsSerializer


# Create your views here.
class ResultListApiView(ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultsSerializer

    def get_queryset(self):
        user = self.request.user
        if user:
            return Result.objects.filter(user=user).first()
        else:
            return Result.objects.none()