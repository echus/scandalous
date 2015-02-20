# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('channel', models.IntegerField(default=0)),
                ('value', models.CharField(max_length=50)),
            ],
            options={
                'ordering': ('channel',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('node', models.IntegerField(primary_key=True, serialize=False, default=0)),
                ('device', models.CharField(max_length=30)),
            ],
            options={
                'ordering': ('node',),
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='channel',
            name='node',
            field=models.ForeignKey(to='nodes.Node'),
            preserve_default=True,
        ),
    ]
