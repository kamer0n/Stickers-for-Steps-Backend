import os

from django.shortcuts import get_object_or_404

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stepsServer.settings')
os.environ.setdefault('USE_S3', 'True')
os.environ.setdefault('DATABASE_URL', 'JEFF')

import django
django.setup()

from friendship.models import Block, Follow, Friend, FriendshipRequest
from steps.models import Profile
from friends.views import user_model

def get_profiles():
    profiles = []
    for i in Profile.objects.all():
        profiles.append(i)
    return profiles

def make_friendships():
    from_user = user_model.objects.get(username='admin')
    for profile in get_profiles():
        try:
            to_user = user_model.objects.get(username=profile.user)
            Friend.objects.add_friend(from_user, to_user)
        except Exception as E:
            pass


def accept_friendships():
    f_requests = FriendshipRequest.objects.all()
    for request in f_requests:
        request.accept()


def delete_friendships():
    user = get_object_or_404(user_model, username='admin')
    friends = Friend.objects.friends(user=user)
    for friend in friends:
        friend.remove()

if __name__ == '__main__':
    print('Starting population script...', end="")
    delete_friendships()
    make_friendships()
    accept_friendships()
    print('DONE')
