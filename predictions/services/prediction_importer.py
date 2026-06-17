import pandas as pd
from predictions.models import Prediction
from matches.models import Match
from users.models import Participant, User


class PredictionImporter:

    def __init__(self, file, participant_name):
        self.file = file
        self.participant_name = participant_name

    def load_data(self):
        return pd.read_excel(self.file, sheet_name="WORLDCUP", header=None)

    def get_or_create_participant(self):
        # ✅ crear usuario automáticamente si no existe
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
        """
        Matching robusto entre Excel y DB
        """
        home_team = str(home_team).strip().lower()
        away_team = str(away_team).strip().lower()

        for match in Match.objects.all():
            db_home = match.home_team.strip().lower()
            db_away = match.away_team.strip().lower()

            if db_home == home_team and db_away == away_team:
                return match

        return None

    def run(self):
        df = self.load_data()
        participant = self.get_or_create_participant()

        created = 0

        for _, row in df.iterrows():
            try:
                # ✅ COLUMNAS (mismo layout que matches)
                home_team = row[26]
                away_team = row[31]
                pred_home = row[28]
                pred_away = row[29]

                # ✅ validar equipos
                if not isinstance(home_team, str) or not isinstance(away_team, str):
                    continue

                home_team = home_team.strip()
                away_team = away_team.strip()

                # ✅ evitar filas basura
                if len(home_team) < 3 or len(away_team) < 3:
                    continue

                # ✅ validar goles
                if not str(pred_home).isdigit() or not str(pred_away).isdigit():
                    continue

                pred_home = int(pred_home)
                pred_away = int(pred_away)

                # ✅ encontrar partido real
                match = self.find_match(home_team, away_team)

                if not match:
                    print(f"❌ NO MATCH FOUND: {home_team} vs {away_team}")
                    continue

                # ✅ evitar duplicados
                if Prediction.objects.filter(
                    participant=participant,
                    match=match
                ).exists():
                    continue

                # ✅ crear predicción
                Prediction.objects.create(
                    participant=participant,
                    match=match,
                    predicted_home_score=pred_home,
                    predicted_away_score=pred_away
                )

                created += 1

            except Exception as e:
                print(f"⚠️ ERROR EN FILA: {e}")
                continue

        return created