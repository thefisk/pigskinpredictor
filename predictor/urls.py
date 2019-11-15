from django.urls import path
from .views import (
    HomeView,
    ResultsView,
    ScheduleView,
    CreatePredictionsView, #New Predictions
    AddPredictionView, #AJAX
    AddBankerView, #AJAX
    ScoreTableView, #Leaderboard
    AboutView, #About
    ScoringView, #Scoring
)
from . import views

urlpatterns = [
    path('',HomeView,name='home'),
    path('results/', ResultsView.as_view(), name='results-view'), #!!!!To implement!!!
    path('schedule/', ScheduleView.as_view(), name='schedule-view'), #!!!To Implement!!!
    path('predict/', CreatePredictionsView, name='new-prediction-view'), #New Predictions
    path('addprediction/',AddPredictionView, name='add-prediction'), #AJAX
    path('addbanker/',AddBankerView, name='add-banker'), #AJAX
    path('scoretable/',ScoreTableView, name='scoretable'), #Leaderboard
    path('about/',AboutView, name='about'), #About
    path('scoring/',ScoringView, name='scoring'), #Scoring
]