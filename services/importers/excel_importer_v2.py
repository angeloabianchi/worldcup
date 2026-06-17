import pandas as pd
from predictions.models import Prediction
from matches.models import Match
from users.models import Participant


class ExcelPredictionImporterV2:

    def __init__(self, file, participant_id):
        self.file = file
        self.participant = Participant.objects.get(id=participant_id)

    def load_raw(self):
        # sin cabecera → tratamos todo como raw
        df = pd.read_excel(self.file, sheet_name="WORLDCUP", header=None)
        return df

    def is_match_row(self, row):
        """
        Detecta filas válidas de partido:
        patrón: [fecha, hora, jornada, equipo1, gol1, gol2, equipo2]
        """
        try:
            # posiciones aproximadas detectadas del Excel
            home = row[3]
            goals_home = row[4]
            goals_away = row[5]
            away = row[6]

            # validaciones básicas
            if (
                isinstance(home, str)
                and isinstance(away, str)
                and str(goals_home).isdigit()
                and str(goals_away).isdigit()
            ):
                return True

        except:
            return False

        return False

    def parse_matches(self, df):
        created = 0

        for _, row in df.iterrows():
            if not self.is_match_row(row):
                continue

            try:
                home_team = str(row[3]).strip()
                away_team = str(row[6]).strip()

                home_score = int(row[4])
                away_score = int(row[5])

                match = Match.objects.filter(
                    home_team__iexact=home_team,
                    away_team__iexact=away_team
                ).first()

                if not match:
                    print(f"No match DB: {home_team} vs {away_team}")
                    continue

                Prediction.objects.update_or_create(
                    participant=self.participant,
                    match=match,
                    defaults={
                        "predicted_home_score": home_score,
                        "predicted_away_score": away_score
                    }
                )

                created += 1

            except Exception as e:
                print(f"Error: {e}")

        return created

    def run(self):
        df = self.load_raw()
        return self.parse_matches(df)