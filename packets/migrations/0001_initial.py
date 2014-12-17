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
                ('pkt_id', models.AutoField(serialize=False, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('channel', models.IntegerField(default=0)),
                ('node', models.IntegerField(default=0)),
                ('data', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ('-pkt_id',),
            },
            bases=(models.Model,),
        ),
    ]
