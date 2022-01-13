from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.forms import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

from .serializers import UserSerializer, UserStickerSerializer, CollectionSerializer, StickerSerializer, \
    AllStickerSerializer, TradesSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAdminUser
from django.contrib.auth.models import User

from friendship.models import Friend

from .models import Profile, Trade, TradeStickerQuantity

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
        key = obj.type + '/' + obj.key
    s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))

    return s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                'Key': key, }, ExpiresIn=100)

def image_upload(request):
    if request.method == 'POST':
        image_file = request.FILES['image_file']
        image_type = request.POST['image_type']
        collection = request.POST['collections']
        rarity = request.POST['rarity']
        desc = request.POST['desc']
        if settings.USE_S3:
            if image_type == 'private':
                upload = UploadPrivate(file=image_file)
            else:
                image_type = 'media'
                upload = Upload(file=image_file)
            upload.save()
            image_url = upload.file.url
            sticker = Sticker(key=upload.file, desc=str(upload.file),
                              name=desc, collection=Collection.objects.get(name=collection),
                              type=image_type, rarity=rarity)
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
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({"error": True, "error_msg": serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)



class ProfileStickersView(APIView):

    def post(self, format=None):
        exists = False
        print(self.request.data)
        try:
            exists = self.request.data['user']
            collection = self.request.data['collection']
        except Exception as e:
            print(e)
        if exists:
            profile = Profile.objects.get(user=User.objects.get(username=exists))
            sticks = profile.get_stickers_by_collection(collection)
            print(sticks)
            serializer = UserStickerSerializer(sticks, many=True)
            #colls = sorted(profile.get_stickers(), key=lambda d: d.collection_id)

            return Response(serializer.data)
        else:
            profile = Profile.objects.get(user=self.request.user)
            serializer = UserStickerSerializer(profile.get_stickers_and_quantities(), many=True)
            return Response(serializer.data)
        #print(profile.get_stickers())
        #serializer = UserStickerSerializer(profile.get_stickers(), many=True)
        #print(serializer.data)
        #return Response(serializer.data)



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
        if profile.steps.steps > (500 << received):
            roll = random.randint(0, 100)
            if 0 <= roll <= 50: rarity = 0
            elif 50 < roll <= 75: rarity = 1
            elif 75 < roll <= 90: rarity = 2
            elif 90 < roll <= 100: rarity = 3
            else: rarity = 0
            stickers = list(Sticker.objects.filter(rarity=rarity))
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
            already_friends = "false"
            if profile == current:
                already_friends = "self"
            elif profile.user in friends_list:
                already_friends = "true"
            if profile.get_sticker_count() != 0:
                board.append({'name': profile.user.username, 'count': profile.get_sticker_count(), 'friends': already_friends})
        board = sorted(board, key=lambda d: d['count'], reverse=True)
        return Response(board)

        #profiles


class ChatToken(APIView):

    def post(self, format=None):
        import stream_chat
        from os import getenv
        user = self.request.user
        user_id = str(user.id)
        api_key = getenv("chatAPI")
        secret_key = getenv("chatSecret")
        server_client = stream_chat.StreamChat(api_key=api_key, api_secret=secret_key)
        server_client.update_user({"id": user_id, "role": "guest"})
        channel = server_client.channel("lobby", "Lobby")
        channel.add_members([{"user_id": user_id}])
        token = server_client.create_token(user_id)
        resp = {"chatToken": token}
        return Response(resp)



class TradeView(APIView):

    def get(self, format=None):

        sent_trades = Trade.objects.filter(sender=self.request.user)
        received_trades = Trade.objects.filter(receiver=self.request.user)
        sent_serializer = TradesSerializer(sent_trades, many=True)
        received_serializer = TradesSerializer(received_trades, many=True)
        trades = {"sent": sent_serializer.data, "received": received_serializer.data}
        return Response(trades)

    def post(self, format=None):
        trade = self.request.data
        trade_id = Trade.objects.get_or_create(
            sender_id=trade['sender'],
            receiver_id=trade['receiver'],
        )
        print(trade_id)
        print('da thinky')
        if not trade_id[1]:
            return tradeResponses('exists', trade_id[0])
        for sticker in trade['sender_stickers']:
            sender_tq = TradeStickerQuantity.objects.get_or_create(
                connected_trade=trade_id[0],
                sticker_id=sticker['sticker'],
                quantity=sticker['quantity'],
            )
        for sticker in trade['receiver_stickers']:
            receiver_tq = TradeStickerQuantity.objects.get_or_create(
                connected_trade=trade_id[0],
                sticker_id=sticker['sticker'],
                quantity=sticker['quantity'],
            )

        #serializer = TradesSerializer(data=request.data)
        #if serializer.is_valid(raise_exception=ValueError):
         #   serializer.create(validated_data=request.data)
         #   return Response(serializer.data, status=status.HTTP_201_CREATED)
        #return Response({"error": True, "error_msg": serializer.error_messages}, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(status=200)

class TradeResponseView(APIView):

    def post(self, format=None):
        #print(request.data)
        print(self.request.data)


        return HttpResponse(status=200)


def tradeResponses(resp, *kwargs):
    if resp == 'exists':
        return Response(
            {"message": f"Trade already exists between {kwargs[0].sender.username} and "
                        f"{kwargs[0].receiver.username}."}
        )
