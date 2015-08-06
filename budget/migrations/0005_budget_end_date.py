# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0004_auto_20150730_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='end_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
