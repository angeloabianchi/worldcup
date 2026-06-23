from collections import defaultdict

from matches.models import Match


def calculate_group_table(group_name):

    matches = Match.objects.filter(
        stage__name=group_name
    )

    table = defaultdict(
        lambda: {
            "team": "",
            "pj": 0,
            "g": 0,
            "e": 0,
            "p": 0,
            "gf": 0,
            "gc": 0,
            "dg": 0,
            "pts": 0,
        }
    )

    for match in matches:

        if (
            match.home_score is None or
            match.away_score is None
        ):
            continue

        home = match.home_team
        away = match.away_team

        hs = match.home_score
        aw = match.away_score

        table[home]["team"] = home
        table[away]["team"] = away

        table[home]["pj"] += 1
        table[away]["pj"] += 1

        table[home]["gf"] += hs
        table[home]["gc"] += aw

        table[away]["gf"] += aw
        table[away]["gc"] += hs

        if hs > aw:

            table[home]["g"] += 1
            table[home]["pts"] += 3

            table[away]["p"] += 1

        elif hs < aw:

            table[away]["g"] += 1
            table[away]["pts"] += 3

            table[home]["p"] += 1

        else:

            table[home]["e"] += 1
            table[away]["e"] += 1

            table[home]["pts"] += 1
            table[away]["pts"] += 1

    rows = list(table.values())

    for row in rows:
        row["dg"] = row["gf"] - row["gc"]

    rows.sort(
        key=lambda x: (
            x["pts"],
            x["dg"],
            x["gf"]
        ),
        reverse=True
    )

    return rows