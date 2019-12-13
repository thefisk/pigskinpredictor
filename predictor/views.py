import json, os
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from accounts.models import User as CustomUser
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import (
    Results,
    Match,
    Prediction,
    ScoresWeek,
    ScoresSeason,
    ScoresAllTime,
    Banker
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

def is_reportviewer(user):
    return user.groups.filter(name='ReportViewers').exists()

@user_passes_test(is_reportviewer)
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
    return render(request, 'predictor/home.html')

class ResultsView(ListView):
    model = Results
    context_object_name = 'results'
    template_name = 'predictor/results.html' # <app>/<model>_viewtype>.html

### View to Display "Add Predictions" Screen
@login_required
def CreatePredictionsView(request):
    week = os.environ['PREDICTWEEK']
    season = os.environ['PREDICTSEASON']
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
    scoreweek = int(os.environ['RESULTSWEEK']) - 1
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

    scoreweek = int(os.environ['RESULTSWEEK']) - 1
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