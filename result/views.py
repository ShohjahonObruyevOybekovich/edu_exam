from rest_framework.generics import ListAPIView

from result.models import Result
from result.serializers import ResultsSerializer


# Create your views here.
class ResultListApiView(ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultsSerializer

    def get_queryset(self):
        user = self.request.query_params.get('user', None)
        if user:
            return Result.objects.filter(user__id=user)
        return Result.objects.none()