from django import template
from django.contrib.auth.models import Group
from predictor.models import Match, ScoresWeek, Results, Team, ScoresSeason, Prediction
from accounts.models import User
import os

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name='corresponding_match')
def corresponding_match(bankerteam):
    week = os.environ['PREDICTWEEK']
    season = os.environ['PREDICTSEASON']
    try:
        matched_game = Match.objects.get(Season=season, Week=week, AwayTeam=bankerteam)
    except Match.DoesNotExist:
        return 0
    else:
        return matched_game.GameID

@register.filter(name='corresponding_home')
def corresponding_home(predgameid):
    try:
        matched_result = Results.objects.get(GameID=predgameid)
    except Results.DoesNotExist:
        return 0
    else:
        return matched_result.HomeScore

@register.filter(name='corresponding_away')
def corresponding_away(predgameid):
    try:
        matched_result = Results.objects.get(GameID=predgameid)
    except Results.DoesNotExist:
        return 0
    else:
        return matched_result.AwayScore

@register.filter(name='division_players')
def division_players(div):
    division = Team.objects.filter(ConfDiv=div)
    try:
        players = User.objects.filter(FavouriteTeam__in=division).count()
    except:
        return 0
    else:
        return players

@register.filter(name='division_total')
def division_total(div):
    division = Team.objects.filter(ConfDiv=div)
    try:
        players = User.objects.filter(FavouriteTeam__in=division)
    except:
        return 0
    total = 0
    for player in players:
        try:
            total += ScoresSeason.objects.get(User=player, Season=int(os.environ['PREDICTSEASON'])).SeasonScore
        except:
            pass
    return total

@register.filter(name='banker_class')
def banker_class(banker):
    if banker.Points > 0:
        return "results-table-right-banker"
    else:
        return "results-table-wrong-banker"

#@register.filter(name='seasonhigh')
#def seasonhigh(user):
#    high = 0
#    for weekscore in ScoresWeek.objects.filter(User=user, Season=os.environ['PREDICTSEASON']):
#        if weekscore.WeekScore > high:
#            high = weekscore.WeekScore
#        else:
#            pass
#    return high