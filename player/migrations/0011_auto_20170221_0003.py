# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-20 18:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('player', '0010_emailverification'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='gcm_token',
            new_name='fcm_token',
        ),
    ]