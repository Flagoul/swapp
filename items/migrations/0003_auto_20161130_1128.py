# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_auto_20161115_2346'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='archived',
        ),
        migrations.AddField(
            model_name='item',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]