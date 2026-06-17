import pandas as pd
from matches.models import Match, Tournament, TournamentStage
from django.utils import timezone


class MatchSeeder:

    def __init__(self, file):
        self.file = file

    def load_data(self):
        return pd.read_excel(self.file, sheet_name="WORLDCUP", header=None)

    def is_valid_team(self, value):
        if not isinstance(value, str):
            return False

        value = value.strip()

        if not value:
            return False

        invalid = [
            "P.", "Pos", "Grupo", "Casa", "Fuera",
            "Descargar Excel Administrador Porra"
        ]

        if any(x.lower() in value.lower() for x in invalid):
            return False

        return True

    def run(self):
        df = self.load_data()

        tournament, _ = Tournament.objects.get_or_create(
            name="World Cup",
            year=2026
        )

        created = 0

        # ✅ SOLO en desarrollo
        Match.objects.all().delete()

        current_stage = None

        for _, row in df.iterrows():
            try:
                # 🔥 1. DETECTAR SI EMPIEZAN ELIMINATORIAS
                row_values = [str(x).lower() for x in row if isinstance(x, str)]

                if any(
                    keyword in value
                    for value in row_values
                    for keyword in [
                        "1/16", "dieciseisavos",
                        "1/8", "octavos",
                        "1/4", "cuartos",
                        "semi",
                        "final"
                    ]
                ):
                    break  # ✅ PARAR completamente el import

                # ✅ 2. DETECTAR GRUPO
                group_value = row[22]

                if isinstance(group_value, str):
                    value = group_value.strip()

                    if value in list("ABCDEFGHIJKL"):
                        current_stage = f"GROUP_{value}"

                # ✅ SOLO si tenemos grupo válido
                if not current_stage:
                    continue

                # ✅ 3. EQUIPOS
                home_team = row[26]  # AB
                away_team = row[31]  # AE

                if not self.is_valid_team(home_team):
                    continue

                if not self.is_valid_team(away_team):
                    continue

                home_team = home_team.strip()
                away_team = away_team.strip()

                # ✅ 4. GOLES (opcionales)
                # gol1 = row[28]
                # gol2 = row[29]

                home_score = None
                away_score = None

                # if str(gol1).isdigit() and str(gol2).isdigit():
                #    home_score = int(gol1)
                #    away_score = int(gol2)

                # ✅ 5. FECHA
                match_date = row[23]

                if pd.isna(match_date):
                    match_date = timezone.now()

                # ✅ 6. STAGE
                stage, _ = TournamentStage.objects.get_or_create(
                    name=current_stage,
                    defaults={"order": 1}
                )

                # ✅ 7. EVITAR DUPLICADOS
                if Match.objects.filter(
                    tournament=tournament,
                    home_team=home_team,
                    away_team=away_team,
                ).exists():
                    continue

                # ✅ 8. CREAR MATCH
                Match.objects.create(
                    tournament=tournament,
                    home_team=home_team,
                    home_score=home_score,
                    away_score=away_score,
                    away_team=away_team,
                    stage=stage,
                    match_date=match_date,
                )

                created += 1

            except Exception:
                continue

        return created