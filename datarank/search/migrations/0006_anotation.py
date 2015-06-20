# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0005_searchrate'),
    ]

    operations = [
        migrations.CreateModel(
            name='Anotation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=200)),
                ('sid', models.CharField(max_length=200)),
                ('keywords', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('comments', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
