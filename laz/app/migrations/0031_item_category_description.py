# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-21 21:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0030_auto_20161221_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='item_category',
            name='description',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
