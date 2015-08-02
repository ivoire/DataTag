# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('path', models.FilePathField(max_length=256, db_index=True, recursive=True, path=settings.MEDIA_ROOT)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, db_index=True)),
                ('is_public', models.BooleanField(default=False)),
                ('is_root', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(to='auth.Group', blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='media',
            name='tags',
            field=models.ManyToManyField(to='DataTag.Tag', blank=True),
        ),
    ]
