from django.contrib.auth.models import User
from django.db import models

from steps.storage_backends import PublicMediaStorage, PrivateMediaStorage


class Collection(models.Model):
    name = models.CharField(max_length=100)
    version = models.IntegerField(default=1)

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
    phonenumber = models.CharField(verbose_name="phone number", max_length=10, null=True)
    birthdate = models.DateField(verbose_name="birth date", null=True)
    #stickers = models.ManyToManyField(StickerQuantity, related_name='stickers')

    def get_sticker_id(self):
        return [x.sticker.id for x in StickerQuantity.objects.filter(profile=self)]

    def get_sticker_collection_id(self):
        return [x.sticker.collection_id for x in StickerQuantity.objects.filter(profile=self)]

    def get_stickers(self):
        return [x.sticker for x in StickerQuantity.objects.filter(profile=self)]

    def __str__(self):
        return self.user.username


class StickerQuantity(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="quantity")

    class Meta:
        verbose_name_plural = "Sticker quantities"
        constraints = [
            models.UniqueConstraint(fields=['profile', 'sticker'], name='unique sticker quantity')
        ]

    def __str__(self):
        return self.sticker.name
