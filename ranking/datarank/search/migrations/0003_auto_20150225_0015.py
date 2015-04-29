# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0002_musictrack'),
    ]

    operations = [
        migrations.AlterField(
            model_name='musictrack',
            name='artist_name',
            field=models.TextField(),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='musictrack',
            name='name',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
