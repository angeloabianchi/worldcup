from django.db import models
from users.models import Participant
from matches.models import Match


class Prediction(models.Model):

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE
    )

    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE
    )

    predicted_home_score = models.IntegerField()

    predicted_away_score = models.IntegerField()

    predicted_home_penalties = models.IntegerField(
        null=True,
        blank=True
    )

    predicted_away_penalties = models.IntegerField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    points = models.IntegerField(
        default=0
    )

    class Meta:
        unique_together = (
            "participant",
            "match"
        )


class KnockoutPrediction(models.Model):

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE
    )

    stage = models.CharField(
        max_length=50
    )

    home_team = models.CharField(
        max_length=100
    )

    away_team = models.CharField(
        max_length=100
    )

    predicted_home_score = models.IntegerField()

    predicted_away_score = models.IntegerField()

    predicted_home_penalties = models.IntegerField(
        null=True,
        blank=True
    )

    predicted_away_penalties = models.IntegerField(
        null=True,
        blank=True
    )

    points = models.IntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )



class BonusPrediction(models.Model):

    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE
    )

    champion = models.CharField(
        max_length=100
    )

    runner_up = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    third_place = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    golden_boot = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    silver_boot = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    bronze_boot = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    golden_ball = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    silver_ball = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    bronze_ball = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )