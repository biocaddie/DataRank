# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0003_auto_20150225_0015'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataset',
            old_name='view_count',
            new_name='Count',
        ),
        migrations.RenameField(
            model_name='dataset',
            old_name='features',
            new_name='ID',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='name_text',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='dataset',
            name='Features',
            field=models.TextField(default=b'NOPE'),
            preserve_default=True,
        ),
    ]
