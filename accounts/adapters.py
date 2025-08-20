from allauth.account.adapter import DefaultAccountAdapter
from predictor.models import PigskinConfig
import os

class AccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=False):
        data = form.cleaned_data
        user.email = data['email']
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.FavouriteTeam = data['fav_team']
        if 'password1' in data:
            user.set_password(data['password1'])
        else:
            user.set_unusable_password()
        self.populate_username(request, user)
        user.save()
        return user

    def is_open_for_signup(self, request):
        try:
            isopen = str(PigskinConfig.objects.get(Name="live").RegistrationOpen).lower()
        except:
            isopen = 'regopenvarmissing'
        return isopen == "true"
        # Returns True or False to manage registration status