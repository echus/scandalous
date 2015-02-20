# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='direction',
            field=models.CharField(default='out', max_length=3, choices=[('in', 'in'), ('out', 'out')]),
            preserve_default=True,
        ),
    ]
