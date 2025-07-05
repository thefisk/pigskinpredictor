from mimetypes import init
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.forms.fields import ChoiceField
from .models import User
from allauth.account.forms import SignupForm
from predictor.models import Team
from django.contrib.auth import get_user_model
from crispy_forms.layout import Layout, Row
from .timezones import timezonelist

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'FavouriteTeam', 'Timezone')

class CustomUserChangeForm(UserChangeForm):

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        self.fields['FavouriteTeam'] = forms.ModelChoiceField(queryset=Team.objects.filter(Active=True), empty_label=None, label='Favourite Team')

    password = ReadOnlyPasswordHashField(label="Password", widget=forms.HiddenInput())
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'FavouriteTeam', 'password', 'Timezone', 'Reminder48', 'PickConfirmation', 'SundayLive')
        exclude = ('username', 'email')

class CustomSignupForm(SignupForm):

    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.initial['timezone'] = 'Europe/London'

    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    fav_team = forms.ModelChoiceField(queryset=Team.objects.filter(Active=True), label='Favourite Team', initial="NFL")
    timezone = forms.ChoiceField(choices = timezonelist, label='Timezone')
    layout = Layout('email',
                    Row('password1', 'password2'),
                    Row('first_name', 'last_name'),
                    Row('fav_team', 'timezone')
                    )
    
    class Meta:
        model = get_user_model()

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.FavouriteTeam = self.cleaned_data['fav_team']
        user.Timezone = self.cleaned_data['timezone']
        user.save()
        return user