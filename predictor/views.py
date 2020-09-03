import json, os
from django.shortcuts import render, get_object_or_404, redirect
from accounts.forms import CustomUserChangeForm
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_GET
from accounts.models import User as CustomUser
from django.contrib.auth.decorators import login_required, user_passes_test
from blog.models import Post
from django.urls import reverse
from .models import (
    Team,
    Results,
    Match,
    Prediction,
    ScoresWeek,
    ScoresSeason,
    ScoresAllTime,
    Banker
)
from .mixins import AjaxFormMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    FormView
)

@require_GET
def RobotsTXT(request):
    lines = [
        "User-Agent: *",
        "Disallow: /"        
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")

def is_superuser(user):
    return user.groups.filter(name='SuperUser').exists()

@user_passes_test(is_superuser, login_url='home')
@login_required
def ReportsView(request):
    reportweek = os.environ['PREDICTWEEK']
    season = os.environ['PREDICTSEASON']
    reportweekseason = season+str(reportweek)

    context = {
        'bankers':Banker.objects.filter(BankSeason=season, BankWeek=reportweek),
        'predictions': Prediction.objects.filter(PredWeek=reportweekseason),
        'matches': Match.objects.filter(Week=reportweek, Season=season)
    }

    template='predictor/report.html'
    return render(request,template,context)

def HomeView(request):
    if request.user.is_authenticated:
        if Post.objects.all().count() > 0:
            latest = Post.objects.all().first().pk
            return redirect('post-latest', latest)
        else:
            return render(request, 'predictor/home.html')
    else:
        return render(request, 'predictor/home.html')

def ProfileView(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid:
            form.save()
            return redirect('profile-amended')
    else:
        try:
            ScoresAllTime.objects.get(User=request.user)
        except ScoresAllTime.DoesNotExist:
            return redirect('profile-newplayer')
        else:
            # if week one, show best from last season
            if int(os.environ['RESULTSWEEK']) == 1:
                profileseason = str((int(os.environ['PREDICTSEASON'])) -1)
            else:
                profileseason = os.environ['PREDICTSEASON']
            form = CustomUserChangeForm(instance=request.user)
            template = "predictor/profile.html"
            seasonhigh = ScoresSeason.objects.get(User=request.user, Season=profileseason).SeasonBest
            seasonlow = ScoresSeason.objects.get(User=request.user, Season=profileseason).SeasonWorst
            seasonpct = ScoresSeason.objects.get(User=request.user, Season=profileseason).SeasonPercentage
            alltimehigh = ScoresAllTime.objects.get(User=request.user).AllTimeBest
            alltimelow = ScoresAllTime.objects.get(User=request.user).AllTimeWorst
            alltimepct = ScoresAllTime.objects.get(User=request.user).AllTimePercentage
            context = {
                'form': form,
                'season': profileseason,
                'seasonhigh': seasonhigh,
                'seasonlow': seasonlow,
                'seasonpct': seasonpct,
                'alltimehigh': alltimehigh,
                'alltimelow': alltimelow,
                'alltimepct': alltimepct,
                }
            return render(request, template, context)

def ProfileNewPlayerView(request):
    form = CustomUserChangeForm(instance=request.user)
    return render(request, 'predictor/profile-newplayer.html', {'form': form})

def ProfileAmendedView(request):
    return render(request, 'predictor/profile-amended.html')

@login_required
def ResultsView(request):
    basescoreweek = int(os.environ['RESULTSWEEK']) - 1
    if basescoreweek < 1:
        return redirect('results-preseason')
    elif basescoreweek > 17:
        scoreweek = 17
    else:
        scoreweek = basescoreweek
    template = 'predictor/results.html'
    PredWeek = int(str(os.environ['PREDICTSEASON'])+str(scoreweek))
    if (Prediction.objects.filter(User=request.user, PredWeek=PredWeek)).count() == 0:
        return redirect('results-didnotplay')   
    else:
        context = {
        'season': os.environ['PREDICTSEASON'],
        'week':scoreweek,
        'weekscore': ScoresWeek.objects.get(User=request.user, Season=os.environ['PREDICTSEASON'], Week=scoreweek).WeekScore,
        'predictions':Prediction.objects.filter(User=request.user, PredWeek=PredWeek),
        'results':Results.objects.filter(Season=os.environ['PREDICTSEASON'], Week=scoreweek)
        }
        return render(request, template, context)

def ResultsDidNotPlayView(request):
    basescoreweek = int(os.environ['RESULTSWEEK']) - 1
    if basescoreweek < 1:
        return redirect('results-preseason')
    elif basescoreweek > 17:
        scoreweek = 17
    else:
        scoreweek = basescoreweek
    template = 'predictor/results-didnotplay.html'
    context = {
        'season': os.environ['PREDICTSEASON'],
        'week':scoreweek,
        'results':Results.objects.filter(Season=os.environ['PREDICTSEASON'], Week=scoreweek)
    }
    return render(request, template, context)

def ResultsPreSeasonView(request):
    template = 'predictor/results-preseason.html'
    return render(request, template)

### View to Display "Add Predictions" Screen
@login_required
def CreatePredictionsView(request):
    week = os.environ['PREDICTWEEK']
    season = os.environ['PREDICTSEASON']
    if int(week) > 17:
        response = redirect('new-year-view')
        return response
    else:
        if len(Prediction.objects.filter(Game__Week=week, Game__Season=season, User=request.user)) == 0:
            template = 'predictor/predict_new.html'
        else:
            response = redirect('amend-prediction-view')
            return response
    context = {
        'bankers':Banker.objects.filter(User=request.user, BankSeason=season),
        'predictions':Prediction.objects.all(),
        'matches':Match.objects.filter(Week=week, Season=season),
        'week':week,
        'season':season,
        'title':'New Prediction'
    }

    return render(request, template, context)

### View to Display "Amend Predictions" Screen
@login_required
def AmendPredictionsView(request):
    week = os.environ['PREDICTWEEK']
    season = os.environ['PREDICTSEASON']
    UserPreds = Prediction.objects.filter(Game__Week=week, Game__Season=season, User=request.user)
    UserBankers = Banker.objects.filter(User=request.user, BankSeason=season)
    UserBankersAmend = UserBankers.exclude(BankWeek=week)
    ClassDict = {}
    for preds in UserPreds:
        ClassDict[preds.Game.GameID] = preds.Winner
    if len(Prediction.objects.filter(Game__Week=week, Game__Season=season, User=request.user)) == 0:
        template = 'predictor/predict_new.html'
    else:
        template = 'predictor/predict_amend.html'
    context = {
        'classdict':ClassDict,
        'bankers':UserBankersAmend,
        'predictions':Prediction.objects.all(),
        'originalbanker':Banker.objects.get(BankWeek=week, BankSeason=season, User=request.user),
        'matches':Match.objects.filter(Week=week, Season=season),
        'week':week,
        'season':season,
        'title':'Amend Predictions'
    }

    return render(request, template, context)

### View to Display after week 17 ###
@login_required
def NewYearView(request):
    nextyear = int(os.environ['PREDICTSEASON'])+1
    player = CustomUser.objects.get(username = request.user.username).first_name
    try:
        score = ScoresSeason.objects.get(User=request.user, Season=os.environ['PREDICTSEASON']).SeasonScore
    except ScoresSeason.DoesNotExist:
        template = "predictor/newplayer_yearend.html"
        context = {
        'nextyear':nextyear,
        'year':os.environ['PREDICTSEASON'],
        'title':'Thanks For Registering',
        'player':player
        }
        return render(request, template, context)
    else:  
        template = 'predictor/year_end.html'
        context = {
            'nextyear':nextyear,
            'year':os.environ['PREDICTSEASON'],
            'score':score,
            'title':'Thanks For Playing',
            'player':player
        }
        return render(request, template, context)

class ScheduleView(ListView):
    model = Match
    context_object_name = 'matches'
    template_name = 'predictor/schedule.html' # <app>/<model>_viewtype>.html

class UserPredictions(ListView):
    model = Prediction
    template_name = 'predictor/user_predictions.html'
    context_object_name = 'predictions'

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        week = self.kwargs.get('week')
        season = self.kwargs.get('season')
        return Prediction.objects.filter(User=user,Game__Week=week,Game__Season=season)

def AboutView(request):
    return render(request, 'predictor/about.html', {'title':'About'})

def ScoringView(request):
    return render(request, 'predictor/scoring.html', {'title':'Scoring'})

### View called by Ajax to add predictions to database.  Returns JSON response.
def AjaxAddPredictionView(request):
        if request.method == 'POST':
            pred_user = request.user
            json_data = json.loads(request.body.decode('utf-8'))
            pred_winner = json_data['pred_winner']
            pred_game_str = json_data['pred_game']
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

### View called by Ajax to add Banker to database.  Returns JSON response.
def AjaxAddBankerView(request):
        if request.method == 'POST':
            banker_user = request.user
            json_data = json.loads(request.body.decode('utf-8'))
            jsongame = json_data['bank_game']
            bankgame = Match.objects.get(GameID=jsongame)
            bankerteam = (Match.objects.get(GameID=jsongame)).AwayTeam
            bankweek = (Match.objects.get(GameID=jsongame)).Week
            response_data = {}
            bankseason = os.environ['PREDICTSEASON']
        
            bankerentry = Banker(User=banker_user, BankWeek=bankweek, BankSeason=bankseason, BankGame=bankgame, BankerTeam=bankerteam)
            bankerentry.save()

            # Set Banker flag to corresponding Prediction
            prediction = Prediction.objects.get(User=banker_user, Game=bankgame)
            prediction.Banker = True
            prediction.save()

            response_data['result'] = 'Banker entry successful!'
            response_data['game'] = str(bankerentry.BankGame)
            response_data['user'] = str(bankerentry.User)
            response_data['winner'] = str(bankerentry.BankerTeam)

            return JsonResponse(response_data)

        else:
            return JsonResponse({"nothing to see": "this isn't happening"})

### View to display latest scoretable for all users
def ScoreTableView(request):
    # Below sets score week to 1 below current results week
    # IE - to pull scores from last completed week 
    basescoreweek = int(os.environ['RESULTSWEEK']) - 1
    if basescoreweek < 1:
        return redirect('scoretable-preseason')
    elif basescoreweek > 17:
        scoreweek = 17
    else:
        scoreweek = basescoreweek
    weekscores = ScoresWeek.objects.filter(Week=scoreweek,Season=os.environ['PREDICTSEASON'])   
    nopreds = CustomUser.objects.all().exclude(id__in=weekscores.values('User'))

    context = {
        'nopreds': nopreds,
        'seasonscores': ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']),
        'weekscores': weekscores,
        'week':scoreweek,
        'season':os.environ['PREDICTSEASON'],
        'title':'Leaderboard'
    }

    return render(request, 'predictor/scoretable.html', context)

### View to display enhanced scoretable for all users
def ScoreTableEnhancedView(request):
    # Below sets score week to 1 below current results week
    # IE - to pull scores from last completed week
    
    basescoreweek = int(os.environ['RESULTSWEEK']) - 1
    if basescoreweek < 1:
        return redirect('scoretable-preseason')
    elif basescoreweek > 17:
        scoreweek = 17
    else:
        scoreweek = basescoreweek

    high = -999
    for weekscore in ScoresWeek.objects.filter(Season=os.environ['PREDICTSEASON']):
        if weekscore.WeekScore > high:
            high = weekscore.WeekScore

    low = 999
    for weekscore in ScoresWeek.objects.filter(Season=os.environ['PREDICTSEASON']):
        if weekscore.WeekScore < low:
            low = weekscore.WeekScore

    worstbest = 999
    for score in ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']):
        if score.SeasonBest < worstbest:
            worstbest = score.SeasonBest

    bestworst = -999
    for score in ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']):
        if score.SeasonWorst > bestworst:
            bestworst = score.SeasonWorst   

    bestbanker = -999
    for seasonscore in ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']):
        if seasonscore.BankerAverage > bestbanker:
            bestbanker = seasonscore.BankerAverage

    worstbanker = 999
    for seasonscore in ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']):
        if seasonscore.BankerAverage < worstbanker:
            worstbanker = seasonscore.BankerAverage

    weekscores = ScoresWeek.objects.filter(Week=scoreweek,Season=os.environ['PREDICTSEASON'])   
    nopreds = CustomUser.objects.all().exclude(id__in=weekscores.values('User'))
    
    context = {
        'nopreds': nopreds,
        'bestbanker': bestbanker,
        'worstbanker': worstbanker,
        'worstweekeveryone': low,
        'bestweekeveryone': high,
        'worstbest': worstbest,
        'bestworst': bestworst,
        'seasonscores': ScoresSeason.objects.filter(Season=os.environ['PREDICTSEASON']),
        'weekscores': ScoresWeek.objects.filter(Week=scoreweek,Season=os.environ['PREDICTSEASON']),
        'week':scoreweek,
        'season':os.environ['PREDICTSEASON'],
        'title':'Leaderboard'
    }

    return render(request, 'predictor/scoretable_enhanced.html', context)

def ScoreTablePreSeasonView(request):
    template = 'predictor/scoretable-preseason.html'
    return render(request, template)

### View called by Ajax to amend predictions in database.  Returns JSON response.
def AjaxAmendPredictionView(request):
        if request.method == 'POST':
            pred_user = request.user
            json_data = json.loads(request.body.decode('utf-8'))
            pred_winner = json_data['pred_winner']
            pred_game_str = json_data['pred_game']
            pred_game = Match.objects.get(GameID=pred_game_str)
            response_data = {}

            oldprediction = Prediction.objects.get(User=pred_user, Game=pred_game)
            oldprediction.delete()
        
            predictionentry = Prediction(User=pred_user, Game=pred_game, Winner=pred_winner)
            predictionentry.save()

            response_data['result'] = 'Prediction entry successful!'
            response_data['game'] = str(predictionentry.Game)
            response_data['user'] = str(predictionentry.User)
            response_data['winner'] = str(predictionentry.Winner)

            return JsonResponse(response_data)

        else:
            return JsonResponse({"nothing to see": "this isn't happening"})

### View called by Ajax to amend Banker to database.  Returns JSON response.
def AjaxAmendBankerView(request):
        if request.method == 'POST':
            banker_user = request.user
            json_data = json.loads(request.body.decode('utf-8'))
            jsongame = json_data['bank_game']
            bankgame = Match.objects.get(GameID=jsongame)
            bankerteam = (Match.objects.get(GameID=jsongame)).AwayTeam
            bankweek = (Match.objects.get(GameID=jsongame)).Week
            response_data = {}
            bankseason = os.environ['PREDICTSEASON']

            oldbanker = Banker.objects.get(User=banker_user, BankWeek=bankweek, BankSeason=bankseason)
            # Remove Banker flag in corresponding Prediction
            oldprediction = Prediction.objects.get(User=banker_user, Game=oldbanker.BankGame)
            oldprediction.Banker = False
            oldprediction.save()
            
            oldbanker.delete()
        
            bankerentry = Banker(User=banker_user, BankWeek=bankweek, BankSeason=bankseason, BankGame=bankgame, BankerTeam=bankerteam)
            bankerentry.save()

            # Set Banker flag to corresponding Prediction
            prediction = Prediction.objects.get(User=banker_user, Game=bankgame)
            prediction.Banker = True
            prediction.save()

            response_data['result'] = 'Banker entry successful!'
            response_data['game'] = str(bankerentry.BankGame)
            response_data['user'] = str(bankerentry.User)
            response_data['winner'] = str(bankerentry.BankerTeam)

            return JsonResponse(response_data)

        else:
            return JsonResponse({"nothing to see": "this isn't happening"})