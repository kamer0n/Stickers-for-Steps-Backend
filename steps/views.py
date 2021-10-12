from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render

import boto3
from botocore.config import Config

s3 = boto3.client('s3', config=Config(signature_version='s3v4'))

from .models import Upload, UploadPrivate, Sticker, Collection


def presignedurl(key):
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
        images = s3.list_objects(Bucket=settings.AWS_STORAGE_BUCKET_NAME)['Contents']
        images = [presignedurl(image['Key']) for image in images if image['Key'].endswith(('.jpeg', '.jpg', '.png'))]
    return render(request, 'upload.html', {
        'images': images
    })