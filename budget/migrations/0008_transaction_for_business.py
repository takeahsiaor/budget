# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0007_budgetcategory_income'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='for_business',
            field=models.BooleanField(default=False),
        ),
    ]
