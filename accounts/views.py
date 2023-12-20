from django.shortcuts import render
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from models import User
from django.shortcuts import redirect

# Create your views here.
class ActiveUsersView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    template_name = 'predictor/active_users.html'
    fields = ['Full_Name','is_active']
    title = 'Active Users'

    def test_func(self):
        return self.request.user.groups.filter(name='SuperUser').exists()

    def handle_no_permission(self):
        return redirect('home')
    
    def get_success_url(self):
        return reverse('home')