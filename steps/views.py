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
        if settings.USE_S3:
            if image_type == 'private':
                upload = UploadPrivate(file=image_file)
            else:
                image_type = 'media'
                upload = Upload(file=image_file)
            upload.save()
            image_url = upload.file.url
            sticker = Sticker(key=upload.file, desc=str(upload.file),
                              name=image_file, collection=Collection.objects.get(id=1),
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

    def get(self, request, format=None):
        profile = Profile.objects.get(user=request.user)
        collections = Collection.objects.all()
        collections = list(collections.values())
        for sticker in profile.get_stickers():
            for collection in collections:
                if "stickers" not in collection:
                    collection['stickers'] = []
                if collection['id'] == sticker.collection_id:
                    url = presignedurl(sticker, combined=False)
                    sticker.key = str(base64.b64encode(requests.get(url).content).decode("utf-8"))
                    collection['stickers'].append(model_to_dict(sticker))

        return JsonResponse(list(collections), safe=False)


class AllStickersView(APIView):
    def get(self, format=None):
        stickers = Sticker.objects.all()
        serializer = AllStickerSerializer(stickers, many=True)
        return Response(serializer.data)
