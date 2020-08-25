from predictor.models import Prediction
from rest_framework import viewsets, mixins
from accounts.models import User
from .permissions import IsSuperUser
from predictor.models import Prediction, Banker
from .serializers import BankerSerializer, UserSerializer, PredictionSerializer
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
from django_filters.rest_framework import DjangoFilterBackend

class UserAPIView(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsSuperUser]
    serializer_class = UserSerializer

class PredictionCSVOrdering(r.CSVRenderer):
    header = ['PredWeek', 'Game', 'User', 'Winner', 'Banker']

class BankersCSVOrdering(r.CSVRenderer):
    header = ['BankSeason', 'BankWeek', 'User', 'BankerTeam']

class PredictionCSVView(mixins.ListModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsSuperUser]
    renderer_classes = (PredictionCSVOrdering, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = PredictionSerializer
    queryset=Prediction.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['User', 'PredWeek', 'PredSeason']

class BankersCSVView(mixins.ListModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsSuperUser]
    renderer_classes = (BankersCSVOrdering, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    queryset = Banker.objects.all()
    serializer_class = BankerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['User', 'BankWeek', 'BankSeason']