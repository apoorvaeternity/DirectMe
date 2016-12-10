# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-03 21:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0005_auto_20161203_2052'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Dock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='DockChart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField(auto_now=True)),
                ('end_time', models.DateTimeField()),
                ('is_success', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='FineLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('dock_chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ship.DockChart')),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='PortType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='RevenueLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_collected', models.IntegerField()),
                ('dock_chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ship.DockChart')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Ship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raid_count', models.IntegerField()),
                ('is_active', models.BooleanField()),
                ('upgraded_at', models.DateTimeField()),
                ('ship_store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ShipStore')),
                ('upgrade_to', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='ship.Ship')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='port',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ship.PortType'),
        ),
        migrations.AddField(
            model_name='port',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dockchart',
            name='port',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ship.Port'),
        ),
        migrations.AddField(
            model_name='dockchart',
            name='ship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ship.Ship'),
        ),
        migrations.AddField(
            model_name='dock',
            name='ship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ship.Ship'),
        ),
        migrations.AddField(
            model_name='dock',
            name='slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Slot'),
        ),
        migrations.AddField(
            model_name='dock',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]