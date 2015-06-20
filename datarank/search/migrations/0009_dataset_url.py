# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0008_auto_20150304_0417'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='Url',
            field=models.TextField(default=b'#'),
            preserve_default=True,
        ),
    ]
