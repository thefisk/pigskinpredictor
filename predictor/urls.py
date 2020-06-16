from django.urls import path, include
from django.conf import settings
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
    NewYearView, #AfterWeek17
    ProfileView,
    ProfileAmendedView,
)
from . import views

urlpatterns = [
    path('',HomeView,name='home'),
    path('profile',ProfileView,name="profile"),
    path('profile-amended', ProfileAmendedView,name="profile-amended"),
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
    path('yearend/',NewYearView, name='new-year-view') #After Week 17
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns