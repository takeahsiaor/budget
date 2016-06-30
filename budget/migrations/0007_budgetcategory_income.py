# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0006_recurringtransactiondef_transaction_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='budgetcategory',
            name='income',
            field=models.BooleanField(default=False),
        ),
    ]
