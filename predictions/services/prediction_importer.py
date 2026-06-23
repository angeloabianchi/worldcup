import pandas as pd

from predictions.models import (
    Prediction,
    KnockoutPrediction,
    BonusPrediction
)

from matches.models import Match
from users.models import Participant, User


class PredictionImporter:

    def __init__(self, file, participant_name):
        self.file = file
        self.participant_name = participant_name

    def load_data(self):
        return pd.read_excel(
            self.file,
            sheet_name="WORLDCUP",
            header=None
        )

    def get_or_create_participant(self):

        user, _ = User.objects.get_or_create(
            username=self.participant_name.lower()
        )

        participant, _ = Participant.objects.get_or_create(
            user=user,
            defaults={
                "display_name": self.participant_name
            }
        )

        return participant

    def find_match(self, home_team, away_team):

        home_team = str(home_team).strip().lower()
        away_team = str(away_team).strip().lower()

        for match in Match.objects.all():

            db_home = match.home_team.strip().lower()
            db_away = match.away_team.strip().lower()

            if (
                db_home == home_team and
                db_away == away_team
            ):
                return match

        return None

    def get_knockout_stage(self, row_number):

        if 100 <= row_number <= 115:
            return "ROUND_OF_32"

        if 119 <= row_number <= 126:
            return "ROUND_OF_16"

        if 130 <= row_number <= 133:
            return "QUARTER_FINAL"

        if 137 <= row_number <= 138:
            return "SEMI_FINAL"

        if row_number == 142:
            return "THIRD_PLACE"

        if row_number == 146:
            return "FINAL"

        return None

    def run(self):

        df = self.load_data()

        participant = self.get_or_create_participant()

        Prediction.objects.filter(
            participant=participant
        ).delete()

        KnockoutPrediction.objects.filter(
            participant=participant
        ).delete()

        BonusPrediction.objects.filter(
            participant=participant
        ).delete()

        BonusPrediction.objects.create(
            participant=participant,

            champion=str(df.iloc[149, 26]).strip(),

            runner_up=str(
                df.iloc[150, 26]
            ).strip(),

            third_place=str(
                df.iloc[151, 26]
            ).strip(),

            golden_boot=str(
                df.iloc[153, 26]
            ).strip(),

            silver_boot=str(
                df.iloc[154, 26]
            ).strip(),

            bronze_boot=str(
                df.iloc[155, 26]
            ).strip(),

            golden_ball=str(
                df.iloc[157, 26]
            ).strip(),

            silver_ball=str(
                df.iloc[158, 26]
            ).strip(),

            bronze_ball=str(
                df.iloc[159, 26]
            ).strip(),
        )

        created = 0

        for _, row in df.iterrows():

            try:

                home_team = row[26]
                away_team = row[31]

                pred_pen_home = row[27]
                pred_home = row[28]
                pred_away = row[29]
                pred_pen_away = row[30]

                if (
                    not isinstance(home_team, str)
                    or
                    not isinstance(away_team, str)
                ):
                    continue

                home_team = home_team.strip()
                away_team = away_team.strip()

                if (
                    len(home_team) < 3
                    or
                    len(away_team) < 3
                ):
                    continue

                if (
                    not str(pred_home).isdigit()
                    or
                    not str(pred_away).isdigit()
                ):
                    continue

                pred_home = int(pred_home)
                pred_away = int(pred_away)

                pred_pen_home = (
                    int(pred_pen_home)
                    if str(pred_pen_home).isdigit()
                    else None
                )

                pred_pen_away = (
                    int(pred_pen_away)
                    if str(pred_pen_away).isdigit()
                    else None
                )

                # FASE DE GRUPOS
                if row.name < 100:

                    match = self.find_match(
                        home_team,
                        away_team
                    )

                    if not match:
                        print(
                            f"❌ NO MATCH FOUND: "
                            f"{home_team} vs {away_team}"
                        )
                        continue

                    Prediction.objects.create(
                        participant=participant,
                        match=match,
                        predicted_home_score=pred_home,
                        predicted_away_score=pred_away,
                        predicted_home_penalties=pred_pen_home,
                        predicted_away_penalties=pred_pen_away,
                    )

                # ELIMINATORIAS
                else:

                    stage = self.get_knockout_stage(
                        row.name
                    )

                    if not stage:
                        continue

                    KnockoutPrediction.objects.create(
                        participant=participant,
                        stage=stage,
                        home_team=home_team,
                        away_team=away_team,
                        predicted_home_score=pred_home,
                        predicted_away_score=pred_away,
                        predicted_home_penalties=pred_pen_home,
                        predicted_away_penalties=pred_pen_away,
                    )

                created += 1

            except Exception as e:
                print(
                    f"⚠️ ERROR EN FILA {row.name}: {e}"
                )
                continue

        return created
