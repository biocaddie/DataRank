# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0009_dataset_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchrate',
            name='sessioncreated',
            field=models.TextField(default=b'-1'),
            preserve_default=True,
        ),
    ]
