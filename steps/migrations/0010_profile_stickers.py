# Generated by Django 3.2.8 on 2021-11-02 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steps', '0009_sticker_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stickers',
            field=models.ManyToManyField(to='steps.Sticker'),
        ),
    ]
