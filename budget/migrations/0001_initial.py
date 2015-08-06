# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Budget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.IntegerField(max_length=2, choices=[(1, b'January'), (2, b'February'), (3, b'March'), (4, b'April'), (5, b'May'), (6, b'June'), (7, b'July'), (8, b'August'), (9, b'September'), (10, b'October'), (11, b'November'), (12, b'December')])),
                ('year', models.IntegerField(help_text=b'Enter full year not just 15', max_length=4)),
                ('projected_spent', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('projected_earned', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BudgetCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2)),
                ('budget', models.ForeignKey(to='budget.Budget')),
            ],
            options={
                'verbose_name_plural': 'Budget Categories',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('notes', models.CharField(max_length=1023, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('transaction_type', models.CharField(default=b'expense', max_length=7, choices=[(b'income', b'Income'), (b'expense', b'Expense')])),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2)),
                ('notes', models.CharField(max_length=1023, null=True, blank=True)),
                ('recurring', models.BooleanField(default=False)),
                ('recurring_interval', models.CharField(blank=True, max_length=127, null=True, choices=[(b'daily', b'Daily'), (b'weekly', b'Weekly'), (b'monthly', b'Monthly'), (b'yearly', b'Yearly')])),
                ('recurring_ordinal', models.IntegerField(max_length=3, null=True, blank=True)),
                ('budget', models.ForeignKey(to='budget.Budget')),
                ('category', models.ForeignKey(to='budget.Category')),
            ],
        ),
        migrations.AddField(
            model_name='budgetcategory',
            name='category',
            field=models.ForeignKey(to='budget.Category'),
        ),
        migrations.AddField(
            model_name='budget',
            name='categories',
            field=models.ManyToManyField(to='budget.Category', null=True, through='budget.BudgetCategory', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='budget',
            unique_together=set([('month', 'year')]),
        ),
    ]
