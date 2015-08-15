# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('DataTag', '0004_make_tag_name_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128, db_index=True)),
                ('description', models.CharField(max_length=1024, null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='tag',
            name='category',
            field=models.ForeignKey(default=None, blank=True, to='DataTag.Category', null=True),
        ),
    ]
