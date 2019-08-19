import json
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from .models import (
    Post,
    Results,
    Match,
    Prediction,
    ScoresWeek,
    ScoresSeason,
    ScoresAllTime
)
from .mixins import AjaxFormMixin
#from .forms import testpredictionform
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView
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

class CreatePredictionsView(LoginRequiredMixin,CreateView):
    template_name = 'predictor/predict.html'

    def get_context_data(self, **kwargs):
        context = super(CreatePredictionsView, self).get_context_data(**kwargs)
        context['predictions'] = Prediction.objects.all()
        context['matches'] = Match.objects.filter(Week=17,Season=2018)
        return context

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

### View to Display "Add Predictions" Screen
def CreatePredictionsViewfunc(request):
    if len(Prediction.objects.filter(Game__Week=17, User=request.user)) == 0:  # <-  MAKE "CURRENT WEEK"
        template = 'predictor/predict_new.html'
    else:
        template = 'predictor/predict_alreadydone.html'
    context = {
        'predictions':Prediction.objects.all(),
        'matches':Match.objects.filter(Week=17, Season=2018)  # <-  NEED TO REPLACE WITH FILTER
    }

    return render(request, template, context)

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

class UserPredictions(ListView):
    model = Prediction
    template_name = 'predictor/user_predictions.html'
    context_object_name = 'predictions'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        week = self.kwargs.get('week')
        season = self.kwargs.get('season')
        return Prediction.objects.filter(User=user,Game__Week=week,Game__Season=season)

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


### View called by Ajax to add predictions to database.  Returns JSON response.
def AddPredictionView(request):
        if request.method == 'POST':
            pred_user = request.user
            json_data = json.loads(request.body.decode('utf-8'))
            pred_winner = json_data['pred_winner']
            pred_game_str = json_data['pred_game']
            print(pred_game_str)
            print(type(pred_game_str))
            pred_game = Match.objects.get(GameID=pred_game_str)
            response_data = {}
        
            predictionentry = Prediction(User=pred_user, Game=pred_game, Winner=pred_winner)
            predictionentry.save()

            response_data['result'] = 'Prediction entry successful!'
            response_data['game'] = str(predictionentry.Game)
            response_data['user'] = str(predictionentry.User)
            response_data['winner'] = str(predictionentry.Winner)

            return JsonResponse(response_data)

        else:
            return JsonResponse({"nothing to see": "this isn't happening"})

### View to display latest scoretable for all users
def ScoreTableView(request):
    context = {
        'seasonscores': ScoresSeason.objects.filter(Season=2018),   # <-  Static Filter in place for testing!!!
        'weekscores': ScoresWeek.objects.filter(Week=17,Season=2018)  # <-  Static Filter in place for testing!!!
    }

    return render(request, 'predictor/scoretable.html', context)