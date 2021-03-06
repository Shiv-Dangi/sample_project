# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-11-20 08:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_auto_20161115_1258'),
    ]

    operations = [
        migrations.CreateModel(
            name='DelBoyCurrentLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delboy_mob', models.CharField(max_length=50)),
                ('delboy_name', models.CharField(max_length=50)),
                ('lastupdated_latitude', models.CharField(max_length=50)),
                ('lastupdated_at', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='DelBoyLocationReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delboy_mob', models.CharField(max_length=50)),
                ('delboy_name', models.CharField(max_length=50)),
                ('date_of_entry', models.DateField()),
                ('coordinate_info', models.CharField(max_length=1000000)),
            ],
        ),
        migrations.DeleteModel(
            name='OtpForApp',
        ),
        migrations.AlterField(
            model_name='allorder',
            name='ordered_items',
            field=models.CharField(max_length=10000),
        ),
        migrations.AlterField(
            model_name='counterorder',
            name='ordered_items',
            field=models.CharField(max_length=10000),
        ),
    ]
