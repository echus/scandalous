# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Packet',
            fields=[
                ('time', models.DateTimeField(serialize=False, auto_now_add=True, primary_key=True)),
                ('channel', models.IntegerField(default=0)),
                ('node', models.IntegerField(default=0)),
                ('data', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-time',),
            },
            bases=(models.Model,),
        ),
    ]
