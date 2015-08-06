# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0002_auto_20150716_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='start_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(default=datetime.date(2015, 7, 17)),
        ),
    ]
