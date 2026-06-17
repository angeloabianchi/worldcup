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

        # ✅ mantener estado del grupo actual
        current_stage = None

        for _, row in df.iterrows():
            try:
                # 🔥 1. DETECTAR GRUPO (columna izquierda del Excel)
                group_value = row[22]  # <-- columna del grupo (A, B, C...)

                if isinstance(group_value, str):
                    value = group_value.strip()

                    value = str(group_value).strip()

                    # ✅ GRUPOS
                    if value in list("ABCDEFGHIJKL"):
                        current_stage = f"{value}"

                    # ✅ DIECISEISAVOS
                    elif "1/16" in value or "dieciseisavos" in value.lower():
                        current_stage = "R16"

                    # ✅ OCTAVOS
                    elif "1/8" in value or "octavos" in value.lower():
                        current_stage = "Octavas de Final"

                    # ✅ CUARTOS
                    elif "1/4" in value or "cuartos" in value.lower():
                        current_stage = "Cuartas de Final"

                    # ✅ SEMI
                    elif "1/2" in value or "semi" in value.lower():
                        current_stage = "Semi-Final"

                    # ✅ 3º y 4º
                    elif "3" in value and "4" in value:
                        current_stage = "Tercero y Cuarto"

                    # ✅ FINAL
                    elif "F" in value.lower():
                        current_stage = "FINAL"

                # 🔥 2. LEER EQUIPOS (columnas reales)
                home_team = row[26]  # AB
                away_team = row[31]  # AE

                if not self.is_valid_team(home_team):
                    continue

                if not self.is_valid_team(away_team):
                    continue

                home_team = home_team.strip()
                away_team = away_team.strip()

                # 🔥 3. GOLES (opcionales)
                gol1 = row[28]  # AC
                gol2 = row[29]  # AD

                home_score = None
                away_score = None

                if str(gol1).isdigit() and str(gol2).isdigit():
                    home_score = int(gol1)
                    away_score = int(gol2)

                # 🔥 4. FECHA
                match_date = row[23]

                if pd.isna(match_date):
                    match_date = timezone.now()

                # 🔥 5. STAGE (grupo o fallback)
                stage_name = current_stage or "GROUP"

                stage, _ = TournamentStage.objects.get_or_create(
                    name=stage_name,
                    defaults={"order": 1}
                )

                # 🔥 6. EVITAR DUPLICADOS
                if Match.objects.filter(
                    tournament=tournament,
                    home_team=home_team,
                    away_team=away_team,
                ).exists():
                    continue

                # 🔥 7. CREAR MATCH
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