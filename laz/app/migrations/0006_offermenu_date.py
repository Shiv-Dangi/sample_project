# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_otpforapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='offermenu',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 5, 13, 19, 51, 385000, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
