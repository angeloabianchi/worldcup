from django.urls import path
from .views import leaderboard, update_results, upload_prediction, seed_matches

urlpatterns = [
    path('upload-prediction/', upload_prediction),
    path('leaderboard/', leaderboard),
    path('update-results/', update_results),
    path('seed-matches/', seed_matches),
]