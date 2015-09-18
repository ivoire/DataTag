# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DataTag', '0006_remove_tag_is_root'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='shortname',
            field=models.CharField(max_length=128, null=True, blank=True),
        ),
    ]
