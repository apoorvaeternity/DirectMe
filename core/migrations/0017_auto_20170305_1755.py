# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-03-05 12:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20170304_1206'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shipstore',
            old_name='ship_id',
            new_name='ship_lvl',
        ),
    ]
