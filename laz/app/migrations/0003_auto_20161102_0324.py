# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20161102_0324'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offer',
            name='description',
            field=models.CharField(max_length=800),
        ),
    ]
