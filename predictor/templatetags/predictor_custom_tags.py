from django import template
from django.core.cache import cache
from django.contrib.auth.models import Group
from predictor.models import Match, ScoresWeek, Results, Team, ScoresSeason, Prediction, PigskinConfig
from accounts.models import User
import os

CacheTTL_1Week = 60 * 60 * 24 * 7
CacheTTL_1Day = 60 * 60 * 24
CacheTTL_1Hour = 60 * 60
CacheTTL_3Hours = 60 * 60 * 3
CacheTTL_5Mins = 60 *5

register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return True if group in user.groups.all() else False

@register.filter(name='pick_logo')
def pick_logo(pred):
    match = Match.objects.get(GameID = pred.Game.GameID)
    if pred.Winner == 'Home':
        return match.HomeTeam.Logo.url
    else:
        return match.AwayTeam.Logo.url

@register.filter(name='corresponding_match')
def corresponding_match(bankerteam):
    week = PigskinConfig.objects.get(Name="live").PredictWeek
    # week = os.environ['PREDICTWEEK']
    season = PigskinConfig.objects.get(Name="live").PredictSeason
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
    cachename = div+'_Players'
    players = cache.get(cachename)
    if not players:
        division = Team.objects.filter(ConfDiv=div)
        try:
            players = User.objects.filter(FavouriteTeam__in=division, is_active=True).count()
        except:
            players = 0
            cache.set(cachename, 0)
        else:
            cache.set(cachename, players, CacheTTL_1Week)
    return players

@register.filter(name='division_total')
def division_total(div):
    cachename = div+'_Total'
    total = cache.get(cachename)
    if not total:
        division = Team.objects.filter(ConfDiv=div)
        try:
            players = User.objects.filter(FavouriteTeam__in=division)
        except:
            cache.set(cachename, 0)
            total = 0
        total = 0
        for player in players:
            try:
                total += ScoresSeason.objects.get(User=player, Season=PigskinConfig.objects.get(Name="live").PredictSeason).SeasonScore
            except:
                pass
        cache.set(cachename, total, CacheTTL_1Week)
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
#    for weekscore in ScoresWeek.objects.filter(User=user, Season=PigskinConfig.objects.get(Name="live").PredictSeason):
#        if weekscore.WeekScore > high:
#            high = weekscore.WeekScore
#        else:
#            pass
#    return high