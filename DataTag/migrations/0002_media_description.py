# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DataTag', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='description',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]
