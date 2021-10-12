# Generated by Django 3.2.8 on 2021-10-15 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('steps', '0003_auto_20211014_2307'),
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Sticker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.FileField(upload_to='')),
                ('desc', models.CharField(max_length=100)),
            ],
        ),
    ]