from django.urls import path
from .views import UserRecordView, ProfileStickersView, AllStickersView, StepsView, LeaderboardView

app_name = 'steps'
urlpatterns = [
    path('user/', UserRecordView.as_view(), name='users'),
    path('usersticks/', ProfileStickersView.as_view(), name='stickers'),
    path('allstickers/', AllStickersView.as_view(), name='allstickers'),
    path('sendsteps/', StepsView.as_view(), name='stepsview'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboardview'),
]
