# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DataTag', '0005_add_categories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='is_root',
        ),
    ]
