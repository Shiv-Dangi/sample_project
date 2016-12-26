# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20161105_1856'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offermenu',
            name='date',
            field=models.DateField(null=True),
        ),
    ]
