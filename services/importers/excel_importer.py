import pandas as pd
from predictions.models import Prediction
from matches.models import Match
from users.models import Participant


class ExcelPredictionImporter:

    def __init__(self, file, participant_id):
        self.file = file
        self.participant = Participant.objects.get(id=participant_id)

    def load_sheet(self):
        return pd.read_excel(self.file, sheet_name="WORLDCUP")

    def normalize_team(self, name):
        return name.strip().lower()

    def find_match(self, home, away):
        return Match.objects.filter(
            home_team__iexact=home,
            away_team__iexact=away
        ).first()

    def parse_matches(self, df):
        predictions_created = 0

        for _, row in df.iterrows():
            try:
                home_team = str(row["Home Team"]).strip()
                away_team = str(row["Away Team"]).strip()

                home_score = int(row["Pred Home"])
                away_score = int(row["Pred Away"])

                match = self.find_match(home_team, away_team)

                if not match:
                    print(f"No match found: {home_team} vs {away_team}")
                    continue

                Prediction.objects.update_or_create(
                    participant=self.participant,
                    match=match,
                    defaults={
                        "predicted_home_score": home_score,
                        "predicted_away_score": away_score
                    }
                )

                predictions_created += 1

            except Exception as e:
                print(f"Error parsing row: {e}")

        return predictions_created

    def run(self):
        df = self.load_sheet()
        count = self.parse_matches(df)
        return count