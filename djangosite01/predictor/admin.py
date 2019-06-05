from django.contrib import admin
from .models import Post, Team, Results, Match, Prediction, Scores

admin.site.register(Post)
admin.site.register(Team)
admin.site.register(Results)
admin.site.register(Match)
admin.site.register(Prediction)
admin.site.register(Scores)