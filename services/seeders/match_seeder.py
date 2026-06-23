import pandas as pd
from matches.models import Match, Tournament, TournamentStage
from django.utils import timezone
from openpyxl.utils.datetime import from_excel


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

        
        stage_orders = {
                "ROUND_OF_32": 1,
                "ROUND_OF_16": 2,
                "QUARTER_FINAL": 3,
                "SEMI_FINAL": 4,
                "THIRD_PLACE": 5,
                "FINAL": 6,
            }

        for _, row in df.iterrows():
            try:
                
                # Solo importar fase de grupos
                if row.name >= 100:
                    break

                # 🔥 1. DETECTAR SI EMPIEZAN ELIMINATORIAS
                row_values = [str(x).lower() for x in row if isinstance(x, str)]

                # if any(
                #     keyword in value
                #     for value in row_values
                #     for keyword in [
                #         "1/16", "dieciseisavos",
                #         "1/8", "octavos",
                #         "1/4", "cuartos",
                #         "semi",
                #         "final"
                #     ]
                # ):
                #     break  # ✅ PARAR completamente el import

                # DIECISEISAVOS
                if row.name == 100:
                    current_stage = "ROUND_OF_32"

                # OCTAVOS
                elif row.name == 119:
                    current_stage = "ROUND_OF_16"

                # CUARTOS
                elif row.name == 130:
                    current_stage = "QUARTER_FINAL"

                # SEMIS
                elif row.name == 137:
                    current_stage = "SEMI_FINAL"

                # 3º/4º PUESTO
                # elif row.name == 140:
                #     current_stage = "THIRD_PLACE"
                elif row.name == 142:
                    print("THIRD PLACE ROW")
                    
                    for i in range(20, 121):
                        value = row[i]

                        if pd.notna(value):
                            print(i, value)


                    current_stage = "THIRD_PLACE"

                # FINAL
                elif row.name == 146:
                    current_stage = "FINAL"

                
                if row.name == 146:
                    print("FINAL ROW")
                    print(row)


                # ✅ 2. DETECTAR GRUPO (solo fase de grupos)
                if row.name < 100:

                    group_value = row[22]

                    if isinstance(group_value, str):
                        value = group_value.strip()

                        if value in list("ABCDEFGHIJKL"):
                            current_stage = f"GROUP_{value}"

                # ✅ SOLO si tenemos grupo válido
                if not current_stage:
                    continue

                # ✅ 3. EQUIPOS
                # home_team = row[26]  # AB
                # away_team = row[31]  # AE

                
                # FASE DE GRUPOS
                if row.name < 100:
                    home_team = row[26]
                    away_team = row[31]
                    match_date = row[23]

                # OCTAVOS, CUARTOS, SEMIS, FINAL
                
                else:

                    # Partido 3º/4º
                    if row.name == 142:
                        home_team = row[3]
                        away_team = row[7]

                    # Resto eliminatorias


                    # FASE DE GRUPOS
                    if row.name < 100:
                        home_team = row[26]
                        away_team = row[31]
                        match_date = row[23]

                    # PARTIDO 3º/4º
                    elif row.name == 142:
                        home_team = row[26]
                        away_team = row[31]
                        match_date = row[23]

                    # RESTO ELIMINATORIAS
                    else:
                        home_team = row[12]
                        away_team = row[13]
                        match_date = row[10]


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


                if pd.isna(match_date):
                    match_date = timezone.now()

                elif isinstance(match_date, (int, float)):
                    match_date = timezone.make_aware(
                        from_excel(match_date)
                    )

                # ✅ 6. STAGE
                stage, _ = TournamentStage.objects.get_or_create(
                    name=current_stage,
                    defaults={
                        "order": stage_orders.get(current_stage, 0)
                    }
                )


                # ✅ 7. EVITAR DUPLICADOS

                if Match.objects.filter(
                    tournament=tournament,
                    home_team=home_team,
                    away_team=away_team,
                    stage=stage,
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

                
                # df = self.load_data()
                # print(df.iloc[100:150, 0:20])



            except Exception as e:
                print(
                    f"ERROR EN FILA {row.name}:",
                    e
                )
                continue


        return created