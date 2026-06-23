from django.db import models

def __str__(self):
    return f"{self.home_team} vs {self.away_team}"

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField()

    def __str__(self):
        return f"{self.name} {self.year}"


class TournamentStage(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    order = models.IntegerField()

    def __str__(self):
        return self.name


class Match(models.Model):

    api_match_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True
    )

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    stage = models.ForeignKey(TournamentStage, on_delete=models.CASCADE)

    home_team = models.CharField(max_length=50)
    away_team = models.CharField(max_length=50)

    match_date = models.DateTimeField()

    # RESULTADOS REALES
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)

    def is_finished(self):
        return self.home_score is not None and self.away_score is not None

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"