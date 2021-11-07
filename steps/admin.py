from django.contrib import admin

from steps.models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phonenumber', 'birthdate', 'collected_stickers')

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


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Upload, UploadAdmin)
admin.site.register(UploadPrivate, UploadPrivateAdmin)
admin.site.register(Sticker, StickerAdmin)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(StickerQuantity, StickerQuantityAdmin)
