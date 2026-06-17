from django.urls import path
from .views import dashboard, matches_view
from .views import (
    upload_prediction,
    seed_matches,
    update_results,
    run_scoring_view,
    leaderboard,
    participant_detail
)

urlpatterns = [
    path('upload-prediction/', upload_prediction),
    path('seed-matches/', seed_matches),
    path('update-results/', update_results),
    path('run-scoring/', run_scoring_view),
    path('leaderboard/', leaderboard),
    path('dashboard/', dashboard),
    path('matches/', matches_view),
    path('participant/<str:name>/', participant_detail),
]