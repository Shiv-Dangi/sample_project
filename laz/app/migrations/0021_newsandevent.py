# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-12-19 05:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_duecreditinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsAndEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('image_url', models.CharField(max_length=200)),
                ('description', models.TextField()),
            ],
        ),
    ]
