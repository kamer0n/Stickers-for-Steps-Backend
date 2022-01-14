import datetime
from django.utils import timezone

from django.contrib.auth.models import User
from django.db import models

from simple_history.models import HistoricalRecords

from steps.storage_backends import PublicMediaStorage, PrivateMediaStorage


class Collection(models.Model):
    name = models.CharField(max_length=100)
    version = models.IntegerField(default=1)
    icon = models.CharField(max_length=100)

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


class Steps(models.Model):
    steps = models.IntegerField(verbose_name="steps")
    stickers_received = models.IntegerField(verbose_name="stickers received")
    history = HistoricalRecords()

    def __str__(self):
        return str(self.steps)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phonenumber = models.CharField(verbose_name="phone number", max_length=10, null=True)
    birthdate = models.DateField(verbose_name="birth date", null=True)
    steps = models.OneToOneField(Steps, on_delete=models.CASCADE, null=True)
    avatar = models.URLField()

    def get_sticker_id(self):
        return [x.sticker.id for x in StickerQuantity.objects.filter(user=self.user)]

    def get_sticker_collection_id(self):
        stickers = StickerQuantity.objects.filter(profile=self)
        return [x.sticker.collection_id for x in stickers]

    def get_stickers(self):
        return [x.sticker for x in StickerQuantity.objects.filter(user=self.user)]

    def get_stickers_and_quantities(self):
        return [(x.sticker.id, x.quantity) for x in StickerQuantity.objects.filter(user=self.user)]

    def get_stickers_by_collection(self, coll_id):
        return [(x.sticker.id, x.quantity) for x in StickerQuantity.objects.filter(user=self.user) if coll_id == x.sticker.collection.id]

    def get_sticker_count(self):
        return len(StickerQuantity.objects.filter(user=self.user))

    def __str__(self):
        return self.user.username


class StickerQuantity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="quantity", null=True)

    class Meta:
        verbose_name_plural = "Sticker quantities"
        constraints = [
            models.UniqueConstraint(fields=['user', 'sticker'], name='unique sticker quantity')
        ]

    def __str__(self):
        return self.sticker.name


class TradeStickerQuantity(models.Model):

    class SendOrRecv(models.IntegerChoices):
        SENT = 1, "SENT"
        RECEIVED = 2, "RECEIVED"

    sticker = models.ForeignKey(Sticker, on_delete=models.CASCADE, related_name='trade_sticker')
    quantity = models.IntegerField(verbose_name="quantity")
    connected_trade = models.ForeignKey('Trade', on_delete=models.CASCADE, blank=True, null=True)
    send_or_recv = models.PositiveSmallIntegerField(choices=SendOrRecv.choices, default=SendOrRecv.SENT)


class Trade(models.Model):

    class TradeStatus(models.IntegerChoices):
        SENT_RECEIVED = 1, "SENT_RECEIVED"
        ACCEPTED = 2, "ACCEPTED"
        DECLINED = 3, "DECLINED"
        COUNTEROFFER = 4, "COUNTER_OFFER"
        INVALID = 5, "INVALID"

    sender = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sender')
    receiver = models.OneToOneField(User, on_delete=models.CASCADE)
    time_sent = models.DateTimeField(default=timezone.now)
    trade_status = models.PositiveSmallIntegerField(choices=TradeStatus.choices, default=TradeStatus.SENT_RECEIVED)

    def get_trade_sticker(self):
        return [x.sticker for x in TradeStickerQuantity.objects.filter(connected_trade=self)]

    def get_sender_stickers(self):
        return [x.sticker for x in TradeStickerQuantity.objects.filter(connected_trade=self, send_or_recv=1)]

    def get_receiver_stickers(self):
        return [x.sticker for x in TradeStickerQuantity.objects.filter(connected_trade=self, send_or_recv=2)]

    def get_trade_validity(self, s_or_r):
        if s_or_r == 's':
            user = self.sender
            send_or_recv = 1
        else:
            user = self.receiver
            send_or_recv = 2
        trade_stickers = TradeStickerQuantity.objects.filter(connected_trade=self, send_or_recv=send_or_recv)
        actual_stickers = StickerQuantity.objects.filter(user=user).values_list('sticker', 'quantity')
        sticker_ids = [x[0] for x in actual_stickers]
        sticker_quantity = [x[1] for x in actual_stickers]
        valid = 0
        for sticker in actual_stickers:
            if sticker[0] in trade_stickers.values_list('sticker_id', flat=True):
                quantity = trade_stickers.get(sticker_id=sticker[0]).quantity
                if (sticker[1] > quantity) and (sticker[1] > 1):
                    valid += 1
                if sticker[1] <= 1:
                    return 4
        if valid == len(trade_stickers):
            return 0
        else:
            return 1


    def __str__(self):
        return "Trade from {} to {}".format(self.sender.username, self.receiver.username)
