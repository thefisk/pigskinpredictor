from django.contrib import admin
from .models import Team, Results, Match ,Prediction, ScoresWeek, ScoresSeason, ScoresAllTime, Banker, Record, AvgScores, LiveGame, PigskinConfig

admin.site.register(Team)
admin.site.register(Results)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(ScoresWeek)
admin.site.register(ScoresSeason)
admin.site.register(ScoresAllTime)
admin.site.register(Banker)
admin.site.register(Record)
admin.site.register(AvgScores)
admin.site.register(LiveGame)
admin.site.register(PigskinConfig)