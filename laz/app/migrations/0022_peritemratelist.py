# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-19 17:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0021_newsandevent'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerItemRateList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=50)),
                ('steam_iron_price', models.CharField(max_length=10, null=True)),
                ('wash_iron_price', models.CharField(max_length=10, null=True)),
                ('dryclean_price', models.CharField(max_length=10, null=True)),
            ],
        ),
    ]
