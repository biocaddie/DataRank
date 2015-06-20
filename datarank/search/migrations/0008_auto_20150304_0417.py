# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0007_auto_20150304_0410'),
    ]

    operations = [
        migrations.CreateModel(
            name='RawComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=200)),
                ('dataset_id', models.CharField(max_length=200)),
                ('keyword', models.TextField()),
                ('comment', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='AnotationRaw',
        ),
    ]
