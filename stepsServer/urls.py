from django.conf import settings
from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.authtoken import views


from steps.models import *
from django.contrib import admin
from rest_framework import routers, serializers, viewsets

import boto3
from botocore.config import Config

from steps.views import image_upload


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'phonenumber', 'birthdate']


class StickerSerializer(serializers.ModelSerializer):
    s3 = boto3.client('s3', config=Config(signature_version='s3v4', region_name='eu-west-2'))
    key = serializers.SerializerMethodField()

    class Meta:
        model = Sticker
        fields = '__all__'

    def get_key(self, obj):
        print(obj.desc)
        return self.s3.generate_presigned_url('get_object', Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                                                                    'Key': obj.type+'/'+obj.desc, }, ExpiresIn=100)


class CollectionSerializer(serializers.ModelSerializer):
    sticker = StickerSerializer(many=True)

    class Meta:
        model = Collection
        fields = ('sticker',)


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def list(self, request, *args, **kwargs):
        return Response([self.serializer_class])


class StickerViewSet(viewsets.ModelViewSet):
    queryset = Sticker.objects.all()
    serializer_class = StickerSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'profiles', ProfileViewSet)
router.register(r'collections', CollectionViewSet)
router.register(r'sticker', StickerViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', image_upload, name='upload'),
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/', include('steps.urls', namespace='api')),
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
    path('api/friendz/', include('friends.urls')),
]
