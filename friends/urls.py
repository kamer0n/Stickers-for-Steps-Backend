from django.urls import path
from friends.views import (
    all_users,
    friendship_accept,
    friendship_add_friend,
    friendship_cancel,
    friendship_reject,
    friendship_request_list,
    friendship_request_list_rejected,
    friendship_requests_detail,
    FriendsListView,
)

app_name = 'friends_api'

urlpatterns = [
    path('users/', view=all_users, name="friendship_view_users"),
    path('friends/', view=FriendsListView.as_view(),
        name="friendship_view_friends",
    ),
    path('friend/add/<slug:to_username>/', view=friendship_add_friend,
        name="friendship_add_friend",
    ),
    path('friend/accept/<int:friendship_request_id>/', view=friendship_accept,
        name="friendship_accept",
    ),
    path('friend/reject/<int:friendship_request_id>/', view=friendship_reject,
        name="friendship_reject",
    ),
    path('friend/cancel/<int:friendship_request_id>/', view=friendship_cancel,
        name="friendship_cancel",
    ),
    path('friend/requests/', view=friendship_request_list,
        name="friendship_request_list",
    ),
    path('friend/requests/rejected/', view=friendship_request_list_rejected,
        name="friendship_requests_rejected",
    ),
    path('friend/request/<int:friendship_request_id>/', view=friendship_requests_detail,
        name="friendship_requests_detail",
    ),
]