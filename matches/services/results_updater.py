import requests
from matches.models import Match


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

    # ASIA
    "Japan": "Japón",
    "South Korea": "Corea del Sur",
    "Korea Republic": "Corea del Sur",
    "Iran": "Irán",
    "Saudi Arabia": "Arabia Saudita",
    "Qatar": "Catar",
    "Australia": "Australia",

    # OTROS POSIBLES
    "New Zealand": "Nueva Zelanda",
    "Haiti": "Haití",
    "Iraq": "Irak",
    "Jordan": "Jordania",
    "Norway": "Noruega",

    # por seguridad
    
    
}


def normalize_team(name):
    return TEAM_MAP.get(name.strip(), name.strip())


def update_match_results():
    url = "https://api.football-data.org/v4/competitions/WC/matches"

    headers = {
        "X-Auth-Token": API_KEY
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    updated = 0

    for match_api in data.get("matches", []):
        try:
            # ✅ SOLO partidos terminados
            if match_api["status"] != "FINISHED":
                continue

            home_team = normalize_team(match_api["homeTeam"]["name"])
            away_team = normalize_team(match_api["awayTeam"]["name"])

            home_score = match_api["score"]["fullTime"]["home"]
            away_score = match_api["score"]["fullTime"]["away"]

            if home_score is None or away_score is None:
                continue

            # ✅ buscar match en tu DB
            match = Match.objects.filter(
                home_team__iexact=home_team,
                away_team__iexact=away_team
            ).first()

            if not match:
                print(f"❌ NO MATCH: {home_team} vs {away_team}")
                continue

            # ✅ actualizar resultado
            match.home_score = home_score
            match.away_score = away_score
            match.save()

            print(f"✅ UPDATED: {home_team} {home_score}-{away_score} {away_team}")
            updated += 1

        except Exception as e:
            print("⚠️ ERROR:", e)
            continue

    return updated
