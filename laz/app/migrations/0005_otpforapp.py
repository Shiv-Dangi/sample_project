# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20161102_0516'),
    ]

    operations = [
        migrations.CreateModel(
            name='OtpForApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile_number', models.CharField(max_length=50)),
                ('otp', models.IntegerField()),
            ],
        ),
    ]
