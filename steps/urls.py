from django.urls import path
from .views import UserRecordView, ProfileStickersView, AllStickersView, StepsView, LeaderboardView, ChatToken, \
    TradeView, TradeResponseView

app_name = 'steps'
urlpatterns = [
    path('user/', UserRecordView.as_view(), name='users'),
    path('usersticks/', ProfileStickersView.as_view(), name='stickers'),
    path('allstickers/', AllStickersView.as_view(), name='allstickers'),
    path('sendsteps/', StepsView.as_view(), name='stepsview'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboardview'),
    path('chattoken/', ChatToken.as_view(), name='chattokenview'),
    path('tradeview/', TradeView.as_view(), name='tradesview'),
    path('traderesponseview/', TradeResponseView.as_view(), name='tradesview'),
]
