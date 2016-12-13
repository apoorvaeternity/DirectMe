# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-13 16:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0010_island_habitable'),
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
                ('end_time', models.DateTimeField(default=None, null=True)),
                ('is_success', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='FineLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.IntegerField()),
                ('dock_chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DockChart')),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('log', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='log', to='core.DockChart')),
            ],
        ),
        migrations.CreateModel(
            name='PortType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('penalizable', models.BooleanField(default=True)),
                ('ownable', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='RevenueLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_collected', models.IntegerField()),
                ('dock_chart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DockChart')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Item')),
            ],
        ),
        migrations.CreateModel(
            name='Ship',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('raid_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('upgraded_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.AlterModelManagers(
            name='shipstore',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='ship',
            name='ship_store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ShipStore'),
        ),
        migrations.AddField(
            model_name='ship',
            name='upgrade_to',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Ship'),
        ),
        migrations.AddField(
            model_name='ship',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='port',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='port', to='core.PortType'),
        ),
        migrations.AddField(
            model_name='port',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='dockchart',
            name='port',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ports', to='core.Port'),
        ),
        migrations.AddField(
            model_name='dockchart',
            name='ship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ships', to='core.Ship'),
        ),
        migrations.AddField(
            model_name='dock',
            name='ship',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Ship'),
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