import os
from predictor.models import Prediction
from rest_framework import viewsets, mixins
from accounts.models import User
from .permissions import IsSuperUser
from predictor.models import Prediction, Banker
from .serializers import (
BankerSerializer,
UserSerializer,
PredictionSerializer,
)
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
from django_filters.rest_framework import DjangoFilterBackend
from allauth.account.models import EmailAddress

class UserAPIView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsSuperUser]
    serializer_class = UserSerializer
    def get_queryset(self):
        verified = EmailAddress.objects.filter(verified=True)
        verifiedemails = []
        for entry in verified:
            verifiedemails.append(entry.email)
        return User.objects.filter(email__in=verifiedemails)

class NoPredsAPIView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsSuperUser]
    serializer_class = UserSerializer
    def get_queryset(self):
        week = os.environ['PREDICTWEEK']
        season = os.environ['PREDICTSEASON']
        predweek = int(season+week)
        haspicked = []
        for pred in Prediction.objects.filter(PredWeek=predweek):
            if pred.User.id not in haspicked:
                haspicked.append(pred.User.id)
        return User.objects.exclude(id__in=haspicked)

class PredictionCSVOrdering(r.CSVRenderer):
    header = ['PredWeek', 'Game', 'User', 'Winner', 'Banker', 'Points']

class BankersCSVOrdering(r.CSVRenderer):
    header = ['BankSeason', 'BankWeek', 'User', 'BankerTeam']

class PredictionCSVView(mixins.ListModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsSuperUser]
    renderer_classes = (PredictionCSVOrdering, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = PredictionSerializer
    queryset=Prediction.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['User', 'PredWeek', 'PredSeason']

class ThisWeekCSVView(mixins.ListModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsSuperUser]
    renderer_classes = (PredictionCSVOrdering, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = PredictionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['User', 'PredWeek', 'PredSeason']
    def get_queryset(self):
        week = os.environ['PREDICTWEEK']
        season = os.environ['PREDICTSEASON']
        predweek = int(season+week)
        return Prediction.objects.filter(PredWeek=predweek)

class LastWeekCSVView(mixins.ListModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsSuperUser]
    renderer_classes = (PredictionCSVOrdering, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    serializer_class = PredictionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['User', 'PredWeek', 'PredSeason']
    def get_queryset(self):
        week = os.environ['PREDICTWEEK']
        season = os.environ['PREDICTSEASON']
        predweek = int(season+week)-1
        return Prediction.objects.filter(PredWeek=predweek)

class BankersCSVView(mixins.ListModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsSuperUser]
    renderer_classes = (BankersCSVOrdering, ) + tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    queryset = Banker.objects.all()
    serializer_class = BankerSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['User', 'BankWeek', 'BankSeason']