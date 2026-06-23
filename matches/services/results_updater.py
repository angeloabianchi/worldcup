import requests

from django.utils.dateparse import parse_datetime

from matches.models import (
    Match,
    Tournament,
    TournamentStage,
)

API_KEY = "9911b2afdf0b4528848da658fab3af57"

TEAM_MAP = {
    # EUROPA
    "Spain": "España",
    "Germany": "Alemania",
    "France": "Francia",
    "England": "Inglaterra",
    "Italy": "Italia",
    "Portugal": "Portugal",
    "Netherlands": "Países Bajos",
    "Belgium": "Bélgica",
    "Croatia": "Croacia",
    "Denmark": "Dinamarca",
    "Switzerland": "Suiza",
    "Poland": "Polonia",
    "Serbia": "Serbia",
    "Austria": "Austria",
    "Czech Republic": "República Checa",
    "Czechia": "República Checa",
    "Scotland": "Escocia",
    "Sweden": "Suecia",
    "Norway": "Noruega",
    "Turkey": "Turquía",
    "Bosnia-Herzegovina": "Bosnia y Herzegovina",

    # SUDAMÉRICA
    "Brazil": "Brasil",
    "Argentina": "Argentina",
    "Uruguay": "Uruguay",
    "Colombia": "Colombia",
    "Chile": "Chile",
    "Ecuador": "Ecuador",
    "Peru": "Perú",
    "Paraguay": "Paraguay",
    "Bolivia": "Bolivia",
    "Curaçao": "Curazao",

    # NORTEAMÉRICA
    "United States": "Estados Unidos",
    "USA": "Estados Unidos",
    "Mexico": "México",
    "Canada": "Canadá",
    "Costa Rica": "Costa Rica",
    "Panama": "Panamá",
    "Honduras": "Honduras",

    # ÁFRICA
    "Morocco": "Marruecos",
    "Senegal": "Senegal",
    "Nigeria": "Nigeria",
    "Cameroon": "Camerún",
    "Ghana": "Ghana",
    "Ivory Coast": "Costa de Marfil",
    "Egypt": "Egipto",
    "Tunisia": "Túnez",
    "Algeria": "Argelia",
    "South Africa": "Sudáfrica",
    "Cape Verde Islands": "Cabo Verde",
    "Congo DR": "RD Congo",

    # ASIA
    "Japan": "Japón",
    "South Korea": "Corea del Sur",
    "Korea Republic": "Corea del Sur",
    "Iran": "Irán",
    "Saudi Arabia": "Arabia Saudita",
    "Qatar": "Catar",
    "Australia": "Australia",
    "Uzbekistan": "Uzbekistán",

    # OTROS
    "New Zealand": "Nueva Zelanda",
    "Haiti": "Haití",
    "Iraq": "Irak",
    "Jordan": "Jordania",
}

STAGE_MAP = {
    "LAST_32": "ROUND_OF_32",
    "LAST_16": "ROUND_OF_16",
    "QUARTER_FINALS": "QUARTER_FINAL",
    "SEMI_FINALS": "SEMI_FINAL",
    "THIRD_PLACE": "THIRD_PLACE",
    "FINAL": "FINAL",
}

STAGE_ORDERS = {
    "ROUND_OF_32": 1,
    "ROUND_OF_16": 2,
    "QUARTER_FINAL": 3,
    "SEMI_FINAL": 4,
    "THIRD_PLACE": 5,
    "FINAL": 6,
}


def map_stage(api_stage):
    return STAGE_MAP.get(api_stage)


def normalize_team(name):

    if not name:
        return None

    name = str(name).strip()

    return TEAM_MAP.get(
        name,
        name
    )


def update_match_results():

    url = "https://api.football-data.org/v4/competitions/WC/matches"

    headers = {
        "X-Auth-Token": API_KEY
    }

    response = requests.get(
        url,
        headers=headers
    )

    data = response.json()

    tournament = Tournament.objects.first()

    updated = 0

    for match_api in data.get("matches", []):

        try:

            api_match_id = match_api["id"]

            home_team = normalize_team(
                match_api.get("homeTeam", {}).get("name")
            )

            away_team = normalize_team(
                match_api.get("awayTeam", {}).get("name")
            )

            # Eliminatorias aún sin clasificados
            if not home_team or not away_team:
                continue

            # Buscar primero por ID oficial
            match = Match.objects.filter(
                api_match_id=api_match_id
            ).first()

            # Compatibilidad con los partidos ya existentes
            if not match:

                match = Match.objects.filter(
                    home_team__iexact=home_team,
                    away_team__iexact=away_team
                ).first()

                if match and not match.api_match_id:

                    match.api_match_id = api_match_id
                    match.save()

            # Crear automáticamente nuevos partidos
            if not match:

                stage_name = map_stage(
                    match_api["stage"]
                )

                # Si es GROUP_STAGE pero no existe,
                # algo raro pasó. Lo ignoramos.
                if not stage_name:
                    continue

                stage, _ = (
                    TournamentStage.objects
                    .get_or_create(
                        name=stage_name,
                        defaults={
                            "order": STAGE_ORDERS[
                                stage_name
                            ]
                        }
                    )
                )

                match = Match.objects.create(
                    api_match_id=api_match_id,
                    tournament=tournament,
                    stage=stage,
                    home_team=home_team,
                    away_team=away_team,
                    match_date=parse_datetime(
                        match_api["utcDate"]
                    )
                )

                print(
                    f"✅ CREATED MATCH: "
                    f"{home_team} vs {away_team}"
                )

            changed = False

            if (
                not match.api_match_id
                or
                match.api_match_id != api_match_id
            ):
                match.api_match_id = api_match_id
                changed = True

            if match_api["status"] == "FINISHED":

                home_score = (
                    match_api["score"]["fullTime"]["home"]
                )

                away_score = (
                    match_api["score"]["fullTime"]["away"]
                )

                if (
                    home_score is not None
                    and
                    away_score is not None
                ):
                    if (
                        match.home_score != home_score
                        or
                        match.away_score != away_score
                    ):
                        match.home_score = home_score
                        match.away_score = away_score
                        changed = True

            if changed:
                match.save()
                updated += 1

                print(
                    f"✅ UPDATED: "
                    f"{home_team} "
                    f"({api_match_id})"
                )

        except Exception as e:

            print(
                f"⚠️ ERROR: {e}"
            )

            continue

    return updated