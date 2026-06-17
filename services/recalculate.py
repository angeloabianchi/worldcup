from matches.models import Match
from predictions.models import Prediction
from scoring.models import Score
from services.scoring_engine import ScoreCalculator


def recalculate_all_scores():
    calculator = ScoreCalculator()

    matches = Match.objects.all()

    for match in matches:
        if not match.is_finished():
            continue

        predictions = Prediction.objects.filter(match=match)

        for p in predictions:
            if match.stage.name == "GROUP":
                points, breakdown = calculator.score_group_stage(p, match)
            else:
                points, breakdown = calculator.score_knockout(p, match)

            Score.objects.update_or_create(
                participant=p.participant,
                match=match,
                defaults={
                    "points": points,
                    "breakdown": breakdown
                }
            )