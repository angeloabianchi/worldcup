from django.contrib import admin
from .models import Score

@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('participant', 'match', 'points')
    list_filter = ('participant',)
