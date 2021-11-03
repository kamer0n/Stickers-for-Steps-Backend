from django.contrib.auth.models import User
from django.db import models

from steps.storage_backends import PublicMediaStorage, PrivateMediaStorage


class Collection(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Sticker(models.Model):
    key = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    desc = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    collection = models.ForeignKey('Collection', on_delete=models.CASCADE, related_name='sticker')
    rarity = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Upload(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PublicMediaStorage())


class UploadPrivate(models.Model):
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(storage=PrivateMediaStorage())


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phonenumber = models.CharField(verbose_name="phone number", max_length=10)
    birthdate = models.DateField(verbose_name="birth date")
    stickers = models.ManyToManyField(Sticker, related_name='stickers')

    def get_sticker_id(self):
        return [x.id for x in self.stickers.all()]

    def get_sticker_collection_id(self):
        return [x.collection_id for x in self.stickers.all()]

    def get_stickers(self):
        return [x for x in self.stickers.all()]
