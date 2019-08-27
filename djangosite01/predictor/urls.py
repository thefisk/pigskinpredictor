from django.urls import path
from .views import (
    PostListView,
    PostDetailView,
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    UserPostListView,
    ResultsView,
    ScheduleView,
    ScoresView,
    UserPredictions,
    CreatePredictionsViewfunc,
    AddPredictionView,
    ScoreTableView,
    AboutView,
)
from . import views

urlpatterns = [
    path('', PostListView.as_view(), name='blog-home'),
    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('results/', ResultsView.as_view(), name='results-view'),
    path('scores/<str:username>', ScoresView.as_view(), name='scores-view'),
    path('schedule/', ScheduleView.as_view(), name='schedule-view'),
    path('predictions/<str:username>/<str:season>/<str:week>', UserPredictions.as_view(), name='user-predictions'), #Still needed?????
    path('predict/', CreatePredictionsViewfunc, name='new-prediction-view'),
    path('addprediction/',AddPredictionView, name='add-prediction'),
    path('scoretable/',ScoreTableView, name='scoretable'),
    path('about/',AboutView, name='about'),
]