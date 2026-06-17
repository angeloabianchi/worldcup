from predictions.models import Prediction


def get_result(h, a):
    if h > a:
        return "HOME"
    elif h < a:
        return "AWAY"
    return "DRAW"


def calculate_points(pred, match):
    ph = pred.predicted_home_score
    pa = pred.predicted_away_score
    rh = match.home_score
    ra = match.away_score

    if rh is None or ra is None:
        return 0

    stage = match.stage.name

    def get_result(h, a):
        if h > a:
            return "HOME"
        elif h < a:
            return "AWAY"
        return "DRAW"

    pred_result = get_result(ph, pa)
    real_result = get_result(rh, ra)

    # ✅ reglas por fase
    rules = {
        "GROUP": {"exact": 3, "sign": 2, "diff": 2},
        "R16": {"exact": 3, "sign": 2, "diff": 2},
        "QF": {"exact": 3, "sign": 2, "diff": 2},
        "SF": {"exact": 3, "sign": 2, "diff": 2},
        "FINAL": {"exact": 4, "sign": 3, "diff": 3},
    }

    if stage.startswith("GROUP"):
        rule = rules["GROUP"]
    else:
        rule = rules.get(stage, rules["GROUP"])

    points = 0

    # ✅ EXACTO
    if ph == rh and pa == ra:
        points += rule["exact"]

    # ✅ DIFERENCIA DE GOLES
    if (ph - pa) == (rh - ra):
        points += rule["diff"]

    # ✅ SIGNO (ganador o empate)
    if pred_result == real_result:
        points += rule["sign"]

    return points


def run_scoring():

    Prediction.objects.update(points=0)
    predictions = Prediction.objects.select_related("match")

    updated = 0

    for pred in predictions:
        match = pred.match

        points = calculate_points(pred, match)

        pred.points = points
        pred.save()

        updated += 1

    return updated