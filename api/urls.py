from django.urls import path, include
from . import views
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register('users', views.UserAPIView, basename='users')
router.register('predictions', views.PredictionCSVView, basename='predictions')
router.register('bankers', views.BankersCSVView, basename='bankers')
router.register('thisweek', views.ThisWeekCSVView, basename='thisweek')
router.register('lastweek', views.LastWeekCSVView, basename='lastweek')
router.register('nopreds', views.NoPredsAPIView, basename='nopreds')

urlpatterns = [
    path('',include(router.urls)),
    path('api-auth',include('rest_framework.urls')),
    path('live-scores', views.LiveScoresAPIView.as_view(), name='live-scores-api')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)