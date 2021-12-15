from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db.models import Prefetch
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from .serializers import UserSerializer, UserStickerSerializer, CollectionSerializer, StickerSerializer, \
    AllStickerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User

from .models import Profile


import base64
import requests

import boto3
from botocore.config import Config

from .models import Upload, UploadPrivate, Sticker, Collection


def presignedurl(obj, combined=True):
    try:
        key = obj.key
    except AttributeError:
        key = obj
        pass
    if not combined:
        key = obj.type + '/' + obj.desc
    s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))

    return s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                'Key': key, }, ExpiresIn=100)

def image_upload(request):
    if request.method == 'POST':
        image_file = request.FILES['image_file']
        image_type = request.POST['image_type']
        collection = request.POST['collections']
        if settings.USE_S3:
            if image_type == 'private':
                upload = UploadPrivate(file=image_file)
            else:
                image_type = 'media'
                upload = Upload(file=image_file)
            upload.save()
            image_url = upload.file.url
            sticker = Sticker(key=upload.file, desc=str(upload.file),
                              name=image_file, collection=Collection.objects.get(name=collection),
                              type=image_type)
            sticker.save()
        else:
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)
        return render(request, 'upload.html', {
            'image_url': image_url
        })
    else:
        s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))
        images = s3.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME)['Contents']
        images = [presignedurl(image['Key']) for image in images if image['Key'].endswith(('.jpeg', '.jpg', '.png'))]
    return render(request, 'upload.html', {
        'images': images
    })


class UserRecordView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "error": True,
                "error_msg": serializer.error_messages,
            },
            status=status.HTTP_400_BAD_REQUEST
        )

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.forms import model_to_dict
from django.http import JsonResponse
from django.shortcuts import render

from .serializers import UserSerializer, UserStickerSerializer, CollectionSerializer, StickerSerializer, \
    AllStickerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User

from friendship.models import Friend

from .models import Profile

import base64
import requests

import random

import boto3
from botocore.config import Config

from .models import Upload, UploadPrivate, Sticker, Collection, StickerQuantity


def presignedurl(obj, combined=True):
    try:
        key = obj.key
    except AttributeError:
        key = obj
        pass
    if not combined:
        key = obj.type + '/' + obj.desc
    s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))

    return s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                'Key': key, }, ExpiresIn=100)

def image_upload(request):
    if request.method == 'POST':
        image_file = request.FILES['image_file']
        image_type = request.POST['image_type']
        collection = request.POST['collections']
        if settings.USE_S3:
            if image_type == 'private':
                upload = UploadPrivate(file=image_file)
            else:
                image_type = 'media'
                upload = Upload(file=image_file)
            upload.save()
            image_url = upload.file.url
            sticker = Sticker(key=upload.file, desc=str(upload.file),
                              name=image_file, collection=Collection.objects.get(name=collection),
                              type=image_type)
            sticker.save()
        else:
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)
        return render(request, 'upload.html', {
            'image_url': image_url
        })
    else:
        s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))
        images = s3.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME)['Contents']
        images = [presignedurl(image['Key']) for image in images if image['Key'].endswith(('.jpeg', '.jpg', '.png'))]
    return render(request, 'upload.html', {
        'images': images
    })


class UserRecordView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=ValueError):
            serializer.create(validated_data=request.data)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "error": True,
                "error_msg": serializer.error_messages,
            },
            status=status.HTTP_400_BAD_REQUEST
        )



class ProfileStickersView(APIView):

    def get(self, format=None):
        profile = Profile.objects.get(user=self.request.user)
        #print(profile.get_stickers())
        serializer = UserStickerSerializer(profile.get_stickers(), many=True)
        print(serializer.data)
        return Response(serializer.data)



class AllStickersView(APIView):
    def get(self, format=None):
        stickers = Sticker.objects.all()
        serializer = AllStickerSerializer(stickers, many=True)
        return Response(serializer.data)


class StepsView(APIView):
    def post(self, request):
        profile = Profile.objects.get(user=self.request.user)
        stepcount = int(request.data['steps'])
        profile.steps.steps = stepcount
        profile.steps.save()
        received = profile.steps.stickers_received
        response = {"target": str(500 << received)}
        if (profile.steps.steps > (500 << received)):
            stickers = list(Sticker.objects.all())
            new_sticker = random.choice(stickers)
            if StickerQuantity.objects.filter(profile=profile, sticker=new_sticker).exists():
                sq = StickerQuantity.objects.get(profile=profile, sticker=new_sticker)
                sq.quantity += 1
                sq.save()
            else:
                StickerQuantity.objects.create(profile=profile, sticker=new_sticker, quantity=1)
            response['sticker'] = StickerSerializer(new_sticker).data
            received += 1
            profile.steps.stickers_received += 1
            profile.steps.save()
        return Response(response)


class LeaderboardView(APIView):

    def post(self, format=None):
        profiles = Profile.objects.all()
        current = Profile.objects.get(user=self.request.user)
        print(current)
        friends_list = Friend.objects.friends(self.request.user)
        print(friends_list)
        board = []
        for profile in profiles:
            already_friends = False
            if profile.user in friends_list:
                already_friends = True
            elif profile.user == current:
                already_friends = 'self'
            if profile.get_sticker_count() != 0:
                board.append({'name': profile.user.username, 'count': profile.get_sticker_count(), 'friends': already_friends})
        board = sorted(board, key=lambda d: d['count'], reverse=True)
        return Response(board)

        #profiles