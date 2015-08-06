# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_budget_end_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringtransactiondef',
            name='transaction_type',
            field=models.CharField(default=b'expense', max_length=7, choices=[(b'income', b'Income'), (b'expense', b'Expense')]),
        ),
    ]
