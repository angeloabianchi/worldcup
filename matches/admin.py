from django.contrib import admin
from .models import Match, Tournament, TournamentStage


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):   
    list_display = (
        'home_team',
        'home_score',
        'away_score',
        'away_team',
        'match_date',
        'stage',
    )
    list_filter = ('stage',)
    search_fields = ('home_team', 'away_team')
    ordering = ('match_date',)
