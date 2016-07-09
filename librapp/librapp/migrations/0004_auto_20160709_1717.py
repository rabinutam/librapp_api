# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-09 17:17
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('librapp', '0003_auto_20160705_0050'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookloan',
            name='date_out',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 7, 9, 17, 16, 2, 66935, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bookloan',
            name='due_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 9, 17, 17, 3, 664964, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='borrower',
            name='email',
            field=models.EmailField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='phone',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='borrower',
            name='ssn',
            field=models.CharField(max_length=9, unique=True),
        ),
        migrations.AlterField(
            model_name='fine',
            name='loan',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='librapp.BookLoan'),
        ),
        migrations.AlterUniqueTogether(
            name='bookloan',
            unique_together=set([('book', 'card_no')]),
        ),
    ]