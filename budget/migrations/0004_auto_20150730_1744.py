# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0003_auto_20150717_2040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recurringtransactiondef',
            name='recurring_interval',
        ),
        migrations.RemoveField(
            model_name='recurringtransactiondef',
            name='recurring_ordinal',
        ),
        migrations.AddField(
            model_name='recurringtransactiondef',
            name='recurrences',
            field=recurrence.fields.RecurrenceField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(),
        ),
    ]
