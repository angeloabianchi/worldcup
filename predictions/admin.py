from django.contrib import admin
from .models import Prediction

@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        'participant',
        'match',
        'predicted_home_score',
        'predicted_away_score'
    )
    list_filter = ('participant',)
    search_fields = ('participant__display_name',)
