from mimetypes import init
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, ReadOnlyPasswordHashField
from django.forms.fields import ChoiceField
from .models import User
from allauth.account.forms import SignupForm, LoginForm
from predictor.models import Team
from django.contrib.auth import get_user_model
from .timezones import timezonelist
from crispy_forms.helper import FormHelper
from crispy_bulma.layout import Layout, Submit, Field
from crispy_forms.layout import Fieldset, Div

class Row(Div):
    css_class = 'row g-3 form-floating mb-3'

class CustomLoginForm(LoginForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'id-loginform'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = 'submit_survey'
        self.form.render_hidden_fields = False

    def login(self, *args, **kwargs):
        return super(CustomLoginForm, self).login(*args, **kwargs)

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
    
    first_name = forms.CharField(max_length=30, label='First Name')
    last_name = forms.CharField(max_length=30, label='Last Name')
    fav_team = forms.ModelChoiceField(queryset=Team.objects.filter(Active=True), label='Favourite Team', initial="NFL")
    timezone = forms.ChoiceField(choices = timezonelist, label='Timezone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['timezone'] = 'Europe/London'
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Fieldset(
            #     'Player Details',
            #     'email',
            #     'password1',
            #     'password2',
            #     'first_name',
            #     'last_name',
            #     'fav_team',
            #     'timezone'
            # ),

            Field('email'),
            Field('password1'),
            Field('password2'),
            Field('first_name'),
            Field('last_name'),
            Field('fav_team', css_class='my_test'),
            Field('timezone'),
            Submit('action', 'Register', css_class='button blue')
        )
        self.helper.form_id = 'id-signup'
        self.helper.form_class = 'fisk_form_class'
        self.helper.form_method = 'post'
        self.helper.form_action = 'register'
    
    class Meta:
        model = get_user_model()

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.FavouriteTeam = self.cleaned_data['fav_team']
        user.Timezone = self.cleaned_data['timezone']
        user.save()
        return user

# class CustomSignupForm(SignupForm):

#     def __init__(self, *args, **kwargs):
#         super(CustomSignupForm, self).__init__(*args, **kwargs)
#         self.initial['timezone'] = 'Europe/London'

#     first_name = forms.CharField(max_length=30, label='First Name')
#     last_name = forms.CharField(max_length=30, label='Last Name')
#     fav_team = forms.ModelChoiceField(queryset=Team.objects.filter(Active=True), label='Favourite Team', initial="NFL")
#     timezone = forms.ChoiceField(choices = timezonelist, label='Timezone')
#     layout = Layout('email',
#                     Row('password1', 'password2'),
#                     Row('first_name', 'last_name'),
#                     Row('fav_team', 'timezone')
#                     )
    
#     class Meta:
#         model = get_user_model()

#     def signup(self, request, user):
#         user.first_name = self.cleaned_data['first_name']
#         user.last_name = self.cleaned_data['last_name']
#         user.FavouriteTeam = self.cleaned_data['fav_team']
#         user.Timezone = self.cleaned_data['timezone']
#         user.save()
#         return user