from rest_framework.decorators import api_view
from django.http import JsonResponse
from rest_framework.response import Response
from services.importers.excel_importer_v2 import ExcelPredictionImporterV2
from services.seeders.match_seeder import MatchSeeder




def leaderboard(request):
    return JsonResponse({"message": "Leaderboard endpoint"})


def update_results(request):
    return JsonResponse({"message": "Update results endpoint"})


@api_view(['POST'])
def upload_prediction(request):
    file = request.FILES.get('file')
    participant_id = request.data.get('participant_id')

    importer = ExcelPredictionImporterV2(file, participant_id)
    count = importer.run()

    return Response({
        "imported": count
    })


@api_view(['POST'])
def seed_matches(request):
    file = request.FILES.get('file')

    if not file:
        return Response({"error": "file required"}, status=400)

    seeder = MatchSeeder(file)
    count = seeder.run()

    return Response({
        "matches_created": count
    })
