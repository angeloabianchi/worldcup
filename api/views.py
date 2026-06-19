from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from services.seeders.match_seeder import MatchSeeder
from predictions.services.prediction_importer import PredictionImporter
from scoring.services.scoring_engine import run_scoring
from matches.services.results_updater import update_match_results

from predictions.models import Prediction, BonusPrediction
from django.db.models import Sum, Case, When, IntegerField

from django.shortcuts import render, get_object_or_404
from matches.models import Match
from users.models import Participant



# ================================
# ✅ UPLOAD PREDICTIONS
# ================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def upload_prediction(request):
    file = request.FILES.get('file')
    name = request.data.get('name')

    if not file or not name:
        return Response(
            {"error": "file and name are required"},
            status=400
        )

    importer = PredictionImporter(file=file, participant_name=name)
    created = importer.run()

    return Response({
        "predictions_created": created
    })


# ================================
# ✅ SEED MATCHES
# ================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def seed_matches(request):
    file = request.FILES.get('file')

    if not file:
        return Response({"error": "file required"}, status=400)

    seeder = MatchSeeder(file)
    count = seeder.run()

    return Response({
        "matches_created": count
    })


# ================================
# ✅ UPDATE RESULTS (API externa)
# ================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def update_results(request):
    updated = update_match_results()
    scored = run_scoring()

    return Response({
        "matches_updated": updated,
        "predictions_scored": scored
    })



# ================================
# ✅ RUN SCORING
# ================================
@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def run_scoring_view(request):
    updated = run_scoring()

    return Response({
        "predictions_scored": updated
    })


# ================================
# ✅ LEADERBOARD
# ================================
@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    data = (
        Prediction.objects
        .values('participant__display_name')
        .annotate(
            total_points=Sum('points'),

            group_points=Sum(
                Case(
                    When(match__stage__name__startswith="GROUP", then='points'),
                    default=0,
                    output_field=IntegerField()
                )
            ),

            knockout_points=Sum(
                Case(
                    When(match__stage__name__in=["R16", "QF", "SF", "FINAL"], then='points'),
                    default=0,
                    output_field=IntegerField()
                )
            ),
        )
        .order_by('-total_points')
    )

    return Response(data)


def dashboard(request):
    return render(request, 'dashboard.html')


def matches_view(request):
    matches = Match.objects.order_by('stage', 'match_date')

    # ✅ separar fases
    group_matches = matches.filter(stage__name__startswith="GROUP")
    knockout_matches = matches.exclude(stage__name__startswith="GROUP")

    return render(request, 'matches.html', {
        'group_matches': group_matches,
        'knockout_matches': knockout_matches
    })


def participant_detail(request, name):
    participant = get_object_or_404(
        Participant,
        display_name=name
    )

    predictions = (
        Prediction.objects
        .filter(participant=participant)
        .select_related('match', 'match__stage')
        .order_by(
            'match__stage__name',
            'match__match_date'
        )
    )

    group_predictions = predictions.filter(
        match__stage__name__startswith="GROUP"
    )

    knockout_predictions = predictions.exclude(
        match__stage__name__startswith="GROUP"
    )

    bonus = BonusPrediction.objects.filter(
        participant=participant
    ).first()

    return render(
        request,
        'participant_detail.html',
        {
            'participant': participant,
            'bonus': bonus,
            'group_predictions': group_predictions,
            'knockout_predictions': knockout_predictions
        }
    )