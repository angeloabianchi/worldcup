from django.contrib import admin
from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):

    list_display = (
        'participant',
        'match_display',
        'match_date',
        'points'
    )

    list_filter = ('participant',)
    search_fields = ('participant__display_name',)
    ordering = ('match__match_date',)

    def match_display(self, obj):
        return f"{obj.match.home_team} {obj.predicted_home_score} vs {obj.predicted_away_score} {obj.match.away_team}"

    match_display.short_description = "Match"

    def match_date(self, obj):
        return obj.match.match_date

    match_date.short_description = "Date"