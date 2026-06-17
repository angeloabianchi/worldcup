from django.db import models
from users.models import Participant
from matches.models import Match


class Score(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    points = models.IntegerField(default=0)
    breakdown = models.JSONField(default=dict)

    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('participant', 'match')