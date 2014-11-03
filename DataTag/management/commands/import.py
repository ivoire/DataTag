# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from DataTag.models import Media, Tag
from DataTag.utils import Configuration

import fnmatch
import os
import yaml


class Command(BaseCommand):
    args = None
    help = 'Synchronize the file system with the database'
    option_list = BaseCommand.option_list

    def handle(self, *args, **kwargs):
        print("Removing old data")
        Media.objects.all().delete()
        Tag.objects.all().delete()

        print("Importing Tags...")
        root_conf = Configuration()
        root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))

        tags = {}
        for tag in root_conf.tags:
            tag_name = tag.name
            print(" - %s" % (tag.name))
            tag = Tag(name=tag.name)
            tag.save()
            tags[tag_name] = tag

        print("Importing the Media")
        for root, dirs, files in os.walk(settings.MEDIA_ROOT, followlinks=True):
            # Parse the local configuration file (if it exists)
            local_conf = Configuration()
            if '.DataTag.yaml' in files:
                local_conf.load(os.path.join(root, '.DataTag.yaml'))

            # Add all files
            for filename in files:
                if filename == '.DataTag.yaml':
                    continue
                path = os.path.join(root, filename)
                print path
                media = Media(path=path)
                media.save()
                for media_conf in local_conf.medias:
                    if fnmatch.fnmatchcase(filename, media_conf.pattern):
                        for tag_name in media_conf.tags:
                            media.tags.add(tags[tag_name])
