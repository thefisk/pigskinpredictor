import django_filters
from models import ScoresWeek, ScoresSeason

class ScoresWeekFilter(django_filters.FilterSet):
    class Meta:
        model = ScoresWeek
        fields = 'Week'

class ScoresSeasonFilter(django_filters.FilterSet):
    class Meta:
        model = ScoresSeason
        fields = 'Season'