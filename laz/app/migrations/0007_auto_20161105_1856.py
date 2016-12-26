# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_offermenu_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offermenu',
            name='date',
            field=models.DateTimeField(null=True),
        ),
    ]
