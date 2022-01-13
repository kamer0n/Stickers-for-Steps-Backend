from django.contrib import admin
from django.contrib.admin import display

from steps.models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phonenumber', 'birthdate', 'collected_stickers', 'steps')

    def collected_stickers(self, obj):
        return "\n".join([a.name for a in obj.get_stickers()])


class UploadAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at', 'file')


class UploadPrivateAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at', 'file')


class StickerAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'key', 'collection', 'type', 'rarity')


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


class StickerQuantityAdmin(admin.ModelAdmin):
    list_display = ('profile', 'sticker', 'quantity',)


class StepsAdmin(admin.ModelAdmin):
    list_display = ('steps', 'history')


class TradeStickerAdmin(admin.ModelAdmin):
    list_display = ('sticker', 'quantity', 'send_or_recv')


class TradeAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'sender_stickers', 'receiver', 'receiver_stickers', 'time_sent', 'trade_status']

    def sender_stickers(self, obj):
        return "\n".join([a.name for a in obj.get_sender_stickers()])

    def receiver_stickers(self, obj):
        return "\n".join([a.name for a in obj.get_receiver_stickers()])


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Upload, UploadAdmin)
admin.site.register(UploadPrivate, UploadPrivateAdmin)
admin.site.register(Sticker, StickerAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(StickerQuantity, StickerQuantityAdmin)
admin.site.register(Steps, StepsAdmin)
admin.site.register(TradeStickerQuantity, TradeStickerAdmin)
admin.site.register(Trade, TradeAdmin)
