from django.urls import path
from .views import UserRecordView, ProfileStickersView, AllStickersView

app_name = 'steps'
urlpatterns = [
    path('user/', UserRecordView.as_view(), name='users'),
    path('usersticks/', ProfileStickersView.as_view(), name='stickers'),
    path('allstickers/', AllStickersView.as_view(), name='allstickers'),
]
