import base64
from urllib.request import urlopen

from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import Profile, Sticker, Collection


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)
        return user

    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['username', 'email']
            )
        ]


class StickerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sticker
        fields = ['id', 'key', 'type', 'desc', 'name', 'rarity', 'collection']


class CollectionSerializer(serializers.ModelSerializer):
    stickers = serializers.SerializerMethodField()

    def get_stickers(self, wow=''):
        obtained_stickers = StickerSerializer(Sticker.objects.filter(
            id__in=self.context['profile'].first().get_sticker_id()), many=True).data
        print(obtained_stickers)
        return obtained_stickers

    class Meta:
        model = Collection
        fields = ('name', 'id', 'stickers',)


class JustCollectionsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Collection
        fields = "__all__"


class UserStickerSerializer(serializers.ModelSerializer):
    #sticker = StickerSerializer(many=True)

    class Meta:
        ordering = ['collection']
        model = Profile
        fields = ('stickers',)
        depth = 1

