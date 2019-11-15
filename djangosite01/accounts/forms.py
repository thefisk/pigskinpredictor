from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from allauth.account.forms import SignupForm
from predictor.models import Team
from django.contrib.auth import get_user_model

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'FavouriteTeam')

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('username', 'email')

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    fav_team = forms.ModelChoiceField(queryset=Team.objects.all(), empty_label=None, label='Favourite Team')
    
    class Meta:
        model = get_user_model()

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.FavouriteTeam = self.cleaned_data['fav_team']
        user.save()
        return user