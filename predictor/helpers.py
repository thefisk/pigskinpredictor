from .models import ScoresWeek

def get_json_week_score(user, week, season):
    try:
        score = ScoresWeek.objects.get(User=user, Week=week, Season=season).WeekScore
    except ScoresWeek.DoesNotExist:
        return 0
    else:
        return score