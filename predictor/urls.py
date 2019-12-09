from django.urls import path
from .views import (
    HomeView,
    ResultsView,
    ScheduleView,
    CreatePredictionsView, #New Predictions
    AmendPredictionsView, #Amend Predictions
    AjaxAddPredictionView, #AJAX
    AjaxAddBankerView, #AJAX
    AjaxAmendPredictionView, #AJAX
    AjaxAmendBankerView, #AJAX
    ScoreTableView, #Leaderboard
    ScoreTableEnhancedView, #Leaderboard
    AboutView, #About
    ScoringView, #Scoring
    ReportsView, #Reports
)
from . import views

urlpatterns = [
    path('',HomeView,name='home'),
    path('results/', ResultsView.as_view(), name='results-view'), #!!!!To implement!!!
    path('schedule/', ScheduleView.as_view(), name='schedule-view'), #!!!To Implement!!!
    path('predict/', CreatePredictionsView, name='new-prediction-view'), #New Predictions
    path('amendpredictions/', AmendPredictionsView, name='amend-prediction-view'), #Amend Predictions
    path('ajaxaddprediction/',AjaxAddPredictionView, name='ajax-add-prediction'), #AJAX
    path('ajaxaddbanker/',AjaxAddBankerView, name='ajax-add-banker'), #AJAX
    path('ajaxamendprediction/',AjaxAmendPredictionView, name='ajax-amend-prediction'), #AJAX
    path('ajaxamendbanker/',AjaxAmendBankerView, name='ajax-amend-banker'), #AJAX
    path('scoretable/',ScoreTableView, name='scoretable'), #Leaderboard
    path('scoretableenhanced/',ScoreTableEnhancedView, name='scoretableenhanced'), #Leaderboard
    path('about/',AboutView, name='about'), #About
    path('scoring/',ScoringView, name='scoring'), #Scoring
    path('report/',ReportsView, name='report'), #Reports
]