import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from steps.models import Profile
from .serializers import FriendshipListSerializer, FriendshipRequestsSerializer

from friendship.exceptions import AlreadyExistsError
from friendship.models import Block, Follow, Friend, FriendshipRequest

from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer

try:
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
except ImportError:
    from django.contrib.auth.models import User

    user_model = User


def get_friendship_context_object_name():
    return getattr(settings, "FRIENDSHIP_CONTEXT_OBJECT_NAME", "user")


def get_friendship_context_object_list_name():
    return getattr(settings, "FRIENDSHIP_CONTEXT_OBJECT_LIST_NAME", "users")


class FriendsListView(APIView):

    def get(self, request, username=None, format=None):
        if username:
            username = username
        else:
            username = request.user

        user = get_object_or_404(user_model, username=username)
        friends = Friend.objects.friends(user)

        friends = Profile.objects.filter(user__in=friends)
        serializer = FriendshipListSerializer(friends, many=True)
        return Response(serializer.data)


@csrf_exempt
@api_view(('POST',))
@login_required
def friendship_add_friend(request, to_username):
    """ Create a FriendshipRequest """
    ctx = {"to_username": to_username}

    if request.method == "POST":
        to_user = user_model.objects.get(username=to_username)
        from_user = request.user
        try:
            Friend.objects.add_friend(from_user, to_user)
        except AlreadyExistsError as e:
            ctx["errors"] = ["%s" % e]
        else:
            return HttpResponse(status=200)

    return JsonResponse(ctx, safe=False)


@csrf_exempt
@api_view(('POST',))
def friendship_accept(request, friendship_request_id):
    """ Accept a friendship request """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=friendship_request_id
        )
        f_request.accept()
        return redirect("friendship_view_friends", username=request.user.username)

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@csrf_exempt
@api_view(('POST',))
def friendship_reject(request, friendship_request_id):
    """ Reject a friendship request """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_received, id=friendship_request_id
        )
        f_request.reject()
        return redirect("friendship_request_list")

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@csrf_exempt
@api_view(('POST',))
@login_required
def friendship_cancel(request, friendship_request_id):
    """ Cancel a previously created friendship_request_id """
    if request.method == "POST":
        f_request = get_object_or_404(
            request.user.friendship_requests_sent, id=friendship_request_id
        )
        f_request.cancel()
        return redirect("friendship_request_list")

    return redirect(
        "friendship_requests_detail", friendship_request_id=friendship_request_id
    )


@api_view(('GET',))
@login_required
def friendship_request_list(request):
    """ View unread and read friendship requests """

    friendship_requests = Friend.objects.requests(request.user)
    # This shows all friendship requests in the database
    # friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=True)
    serializer = FriendshipRequestsSerializer(friendship_requests, many=True)
    return Response(serializer.data)


@api_view(('GET',))
@login_required
def friendship_request_list_rejected(request):
    """ View rejected friendship requests """
    # friendship_requests = Friend.objects.rejected_requests(request.user)
    friendship_requests = FriendshipRequest.objects.filter(rejected__isnull=False)
    serializer = FriendshipRequestsSerializer(friendship_requests, many=True)

    return Response(serializer.data)


@api_view(('POST',))
@login_required
def friendship_requests_detail(request, friendship_request_id):
    """ View a particular friendship request """
    f_request = get_object_or_404(FriendshipRequest, id=friendship_request_id)
    serializer = FriendshipRequestsSerializer(f_request)
    return Response(serializer.data)


def all_users(request, template_name="friendship/user_actions.html"):
    users = user_model.objects.all()

    return render(
        request, template_name, {get_friendship_context_object_list_name(): users}
    )
