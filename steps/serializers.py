import base64
from urllib.request import urlopen

import boto3
import requests
from botocore.config import Config
from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from stepsServer import settings
from .models import Profile, Sticker, Collection, Steps


class UserSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        steps = Steps.objects.create(steps=0, stickers_received=0)
        Profile.objects.create(user=user, steps=steps,
                               avatar="http://0.0.0.0:3000/api/avataaars/" + user.username + ".svg",
                               )

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
        url = self.s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                    'Key': obj.type+'/'+obj.key, }, ExpiresIn=100)
        return str(base64.b64encode(requests.get(url).content).decode("utf-8"))


class CollectionSerializer(serializers.ModelSerializer):
    stickers = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ('name', 'id', 'stickers',)

    def get_stickers(self, wow=''):
        obtained_stickers = StickerSerializer(Sticker.objects.filter(
            id__in=self.context['profile'].first().get_sticker_id()), many=True).data
        return obtained_stickers



class JustCollectionsSerializer(serializers.ModelSerializer):
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = "__all__"

    def get_icon(self, obj):
        s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))
        url = s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                   'Key': 'media' + '/' + obj.icon, }, ExpiresIn=100)
        return str(base64.b64encode(requests.get(url).content).decode("utf-8"))


class UserStickerSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()

    class Meta:
        model = Sticker
        fields = ('id', 'quantity')

    def get_id(self, obj):
        return obj[0]

    def get_quantity(self, obj):
        return obj[1]


