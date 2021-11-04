from django.contrib.auth.models import User
from friendship.models import Friend, FriendshipRequest
from rest_framework import serializers

from steps.models import Profile


class FriendshipListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = '__all__'
        #depth = 1

    def get_user(self, context):
        return context.user.username


class FriendshipRequestsSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendshipRequest
        fields = '__all__'
