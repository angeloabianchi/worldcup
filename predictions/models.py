from django.db import models
from users.models import Participant
from matches.models import Match


class Prediction(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)

    predicted_home_score = models.IntegerField()
    predicted_away_score = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant} - {self.match}"


class BonusPrediction(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)

    champion = models.CharField(max_length=50)
    runner_up = models.CharField(max_length=50)
    third_place = models.CharField(max_length=50)

    # ejemplo premios
    best_player = models.CharField(max_length=50, null=True, blank=True)