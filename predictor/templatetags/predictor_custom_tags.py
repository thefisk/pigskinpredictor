from django import template
from django.contrib.auth.models import Group
from predictor.models import Match
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