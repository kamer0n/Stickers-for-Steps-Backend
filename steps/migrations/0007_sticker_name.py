# Generated by Django 3.2.8 on 2021-10-15 19:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steps', '0006_sticker_collection'),
    ]

    operations = [
        migrations.AddField(
            model_name='sticker',
            name='name',
            field=models.CharField(default='goku', max_length=100),
            preserve_default=False,
        ),
    ]
