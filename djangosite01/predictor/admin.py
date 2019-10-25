from django.contrib import admin
from .models import Post, Team, Results, Match ,Prediction, ScoresWeek, ScoresSeason, ScoresAllTime, Banker

admin.site.register(Post)
admin.site.register(Team)
admin.site.register(Results)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(ScoresWeek)
admin.site.register(ScoresSeason)
admin.site.register(ScoresAllTime)
admin.site.register(Banker)