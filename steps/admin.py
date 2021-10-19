from django.contrib import admin

from steps.models import *


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phonenumber', 'birthdate')


class UploadAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at', 'file')


class UploadPrivateAdmin(admin.ModelAdmin):
    list_display = ('uploaded_at', 'file')


class StickerAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc', 'key', 'collection', 'type')


class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Upload, UploadAdmin)
admin.site.register(UploadPrivate, UploadPrivateAdmin)
admin.site.register(Sticker, StickerAdmin)
admin.site.register(Collection, CollectionAdmin)
