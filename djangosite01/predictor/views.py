from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse
from django.contrib.auth.models import User
from .models import Post, Results, Match, Prediction
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

def home(request):
    context = {
        'posts':Post.objects.all()
    }
    return render(request, 'predictor/home.html', context)

class ResultsView(ListView):
    model = Results
    context_object_name = 'results'
    template_name = 'predictor/results.html' # <app>/<model>_viewtype>.html

class ScoresView(ListView):
    #model = Prediction
    #context_object_name = 'predictions'
    template_name = 'predictor/scores.html' # <app>/<model>_viewtype>.html
    
    def get_context_data(self, **kwargs):
        context = super(ScoresView, self).get_context_data(**kwargs)
        context['predictions'] = Prediction.objects.all()
        context['results'] = Results.objects.all()
        return context
        
    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Prediction.objects.filter(User=user).order_by('Game')

class ScheduleView(ListView):
    model = Match
    context_object_name = 'matches'
    template_name = 'predictor/schedule.html' # <app>/<model>_viewtype>.html

class PostListView(ListView):
    model = Post
    template_name = 'predictor/home.html' # <app>/<model>_viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5 # no need to import Paginator with class based views, this property takes care of it for you

class UserPostListView(ListView):
    model = Post
    template_name = 'predictor/user_posts.html' # <app>/<model>_viewtype>.html
    context_object_name = 'posts'
    paginate_by = 5 # no need to import Paginator with class based views, this property takes care of it for you

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-date_posted')

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin,CreateView): #can't use decorators (for login required etc) on class based views
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView): #can't use decorators (for login required etc) on class based views
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self): #function to stop others updating your blog posts - user test
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Post
    success_url = '/'

    def test_func(self): #function to stop others updating your blog posts - user test
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

def about(request):
    return render(request, 'predictor/about.html', {'title':'About'})