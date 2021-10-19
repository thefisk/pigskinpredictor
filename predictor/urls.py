from django.urls import path, include, re_path
from django.conf import settings
from .views import (
    HomeView, RecordDeleteView,
    ResultsView,
    ResultsPreSeasonView,
    ResultsDidNotPlayView,
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
    Week18View, #LastWeek
    ProfileView,
    ProfileAmendedView,
    ProfileNewPlayerView,
    ScoreTablePreSeasonView,
    DivisionTableView,
    RobotsTXT,
    AjaxDeadlineVerification,
    AddRecordView,
    AmendRecordView,
    RecordsView,
    RecordDeleteView,
    LiveScoresView
)
from . import views
from django.views.generic import RedirectView

def trigger_error(request):
    division_by_zero = 1 / 0

urlpatterns = [
    path('sentry-debug/', trigger_error),
    path('',HomeView,name='home'),
    path('add-record', AddRecordView.as_view(extra_context={'title': 'Add Record'}), name="add-record"),
    path('records/', RecordsView.as_view(extra_context={'title': 'Record Books'}), name="records"),
    path('<int:pk>/delete/', RecordDeleteView.as_view(extra_context={'title': 'Delete Record'}), name='record-delete'),
    re_path(r'^amend-record/(?P<pk>\d+)/$', AmendRecordView.as_view(extra_context={'title': 'Amend Record'}), name="amend-record"),
    path('robots.txt', RobotsTXT),
    path('profile/',ProfileView,name="profile"),
    path('profile-amended/', ProfileAmendedView,name="profile-amended"),
    path('profile-newplayer/', ProfileNewPlayerView,name="profile-newplayer"),
    path('results/', ResultsView, name='results'),
    path('results-didnotplay/', ResultsDidNotPlayView, name='results-didnotplay'),
    path('results-preseason/', ResultsPreSeasonView, name='results-preseason'),
    path('predict/', CreatePredictionsView, name='new-prediction-view'), #New Predictions
    path('amendpredictions/', AmendPredictionsView, name='amend-prediction-view'), #Amend Predictions
    path('ajaxaddprediction/',AjaxAddPredictionView, name='ajax-add-prediction'), #AJAX
    path('ajaxaddbanker/',AjaxAddBankerView, name='ajax-add-banker'), #AJAX
    path('ajaxamendprediction/',AjaxAmendPredictionView, name='ajax-amend-prediction'), #AJAX
    path('ajaxamendbanker/',AjaxAmendBankerView, name='ajax-amend-banker'), #AJAX
    path('scoretable/',ScoreTableView, name='scoretable'), #Leaderboard
    path('scoretableenhanced/',ScoreTableEnhancedView, name='scoretableenhanced'), #Leaderboard
    path('scoretable-preseason/', ScoreTablePreSeasonView, name='scoretable-preseason'),
    path('scoretable-division/', DivisionTableView, name='scoretable-division'),
    path('about/',AboutView, name='about'), #About
    path('scoring/',ScoringView, name='scoring'), #Scoring
    path('report/',ReportsView, name='report'), #Reports
    path('yearend/',NewYearView, name='new-year-view'), #After Week 18
    path('week18/',Week18View, name='week-18-view'), #After Week 18
    path('ajaxdeadlineverification/',AjaxDeadlineVerification, name='report'), #AJAX
    path('live-scores/', LiveScoresView, name='live-scores'),
    re_path(r'^favicon', RedirectView.as_view(url='https://pigskinpredictor.s3.eu-west-2.amazonaws.com/static/favicon.ico')) #Favicon Redirect
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns