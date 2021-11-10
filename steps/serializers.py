import base64
from urllib.request import urlopen

import boto3
from botocore.config import Config
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from stepsServer import settings
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


class AllStickerSerializer(serializers.ModelSerializer):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))
    key = serializers.SerializerMethodField()

    class Meta:
        model = Sticker
        fields = '__all__'

    def get_key(self, obj):
        return self.s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                    'Key': obj.type+'/'+obj.desc, }, ExpiresIn=100)


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

