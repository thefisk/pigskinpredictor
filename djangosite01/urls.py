from django.contrib import admin
from django.contrib.auth import views as auth_views 
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from debug_toolbar.toolbar import debug_toolbar_urls

urlpatterns = [
    path('accounts/', include('allauth.urls')),
    path('admin/', admin.site.urls),
    path('', include('predictor.urls')), #empty route will define home route
    path('api/',include('api.urls')), #API URLs
    path('updates/', include('blog.urls')), #Blog updates
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'), #template name argument added to overwrite default of registration/login.html
    path('logout/', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'), #this is a 'class based view', by default logout will return the admin screen login screen (not desirable)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'), #this is a 'class based view', by default logout will return the admin screen login screen (not desirable)
    path('password-reset/done', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'), #this is a 'class based view', by default logout will return the admin screen login screen (not desirable)
    path('password-reset-confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'), #this is a 'class based view', by default logout will return the admin screen login screen (not desirable)
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'), #this is a 'class based view', by default logout will return the admin screen login screen (not desirable)
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += debug_toolbar_urls()
