# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-19 19:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0025_laundryplans'),
    ]

    operations = [
        migrations.AddField(
            model_name='laundryplans',
            name='plans_code',
            field=models.CharField(max_length=50, null=True),
        ),
    ]