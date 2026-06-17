class ScoreCalculator:

    def get_result_sign(self, home, away):
        if home > away:
            return "1"
        elif home < away:
            return "2"
        return "X"

    def score_group_stage(self, prediction, match):
        points = 0
        breakdown = {}

        real_home = match.home_score
        real_away = match.away_score

        pred_home = prediction.predicted_home_score
        pred_away = prediction.predicted_away_score

        # Resultado exacto
        if real_home == pred_home and real_away == pred_away:
            points += 5
            breakdown["exact"] = 5

        # Signo (1X2)
        if self.get_result_sign(real_home, real_away) == \
           self.get_result_sign(pred_home, pred_away):
            points += 2
            breakdown["sign"] = 2

        # Diferencia de goles
        if (real_home - real_away) == (pred_home - pred_away):
            points += 2
            breakdown["goal_diff"] = 2

        return points, breakdown

    def score_knockout(self, prediction, match):
        points = 0
        breakdown = {}

        real_home = match.home_score
        real_away = match.away_score

        pred_home = prediction.predicted_home_score
        pred_away = prediction.predicted_away_score

        # Signo
        if self.get_result_sign(real_home, real_away) == \
           self.get_result_sign(pred_home, pred_away):
            points += 2
            breakdown["sign"] = 2

        # Diferencia
        if (real_home - real_away) == (pred_home - pred_away):
            points += 2
            breakdown["diff"] = 2

        # Exacto
        if real_home == pred_home and real_away == pred_away:
            points += 3
            breakdown["exact"] = 3

        return points, breakdown