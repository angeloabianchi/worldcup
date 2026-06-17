from django.contrib import admin
from django.db.models import Sum
from django.utils.html import format_html
from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):

    list_display = (
        'ranking_position',
        'display_name',
        'colored_points',
    )

    search_fields = ('display_name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(total_points_sum=Sum('prediction__points')).order_by('-total_points_sum')

    def ranking_position(self, obj):
        queryset = list(self.get_queryset(None))
        position = queryset.index(obj) + 1

        if position == 1:
            return "🥇"
        elif position == 2:
            return "🥈"
        elif position == 3:
            return "🥉"
        return position

    ranking_position.short_description = "Rank"

    def colored_points(self, obj):
        points = obj.total_points_sum or 0

        if points >= 40:
            color = "green"
        elif points >= 25:
            color = "blue"
        elif points >= 10:
            color = "orange"
        else:
            color = "gray"

        return format_html(
            '<b style="color:{}; font-size:14px">{} pts</b>',
            color,
            points
        )

    colored_points.short_description = "Points"
