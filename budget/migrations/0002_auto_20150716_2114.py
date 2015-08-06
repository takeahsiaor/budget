# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecurringTransactionDef',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2)),
                ('notes', models.CharField(max_length=1023, null=True, blank=True)),
                ('recurring_interval', models.CharField(blank=True, max_length=127, null=True, choices=[(b'daily', b'Daily'), (b'weekly', b'Weekly'), (b'monthly', b'Monthly'), (b'yearly', b'Yearly')])),
                ('recurring_ordinal', models.IntegerField(null=True, blank=True)),
                ('last_update', models.DateField(auto_now=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('category', models.ForeignKey(to='budget.Category')),
            ],
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='recurring',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='recurring_interval',
        ),
        migrations.RemoveField(
            model_name='transaction',
            name='recurring_ordinal',
        ),
        migrations.AlterField(
            model_name='budget',
            name='month',
            field=models.IntegerField(choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')]),
        ),
        migrations.AlterField(
            model_name='budget',
            name='year',
            field=models.IntegerField(help_text=b'Enter full year not just 15'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(default=datetime.date(2015, 7, 16)),
        ),
        migrations.AlterUniqueTogether(
            name='budgetcategory',
            unique_together=set([('budget', 'category')]),
        ),
        migrations.AddField(
            model_name='transaction',
            name='recurring_transaction_def',
            field=models.ForeignKey(blank=True, to='budget.RecurringTransactionDef', null=True),
        ),
    ]
