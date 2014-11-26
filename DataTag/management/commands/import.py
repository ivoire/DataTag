# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from DataTag.models import Media, Tag
from DataTag.utils import Configuration

import fnmatch
import os


class Command(BaseCommand):
    args = None
    help = 'Synchronize the file system with the database'
    option_list = BaseCommand.option_list

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print("Removing old data")
        Media.objects.all().delete()
        Tag.objects.all().delete()

        print("Importing Tags...")
        root_conf = Configuration()
        root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))

        tags = {}
        for tag_conf in root_conf.tags:
            print(" - %s" % (tag_conf.name))
            tag = Tag(name=tag_conf.name, is_public=tag_conf.public)
            tag.save()
            # Add groups
            for group in tag_conf.groups:
                print("   - %s" % (group))
                tag.groups.add(Group.objects.get(name=group))

            tags[tag_conf.name] = tag

        print("Importing the Media")
        for root, _, files in os.walk(settings.MEDIA_ROOT,
                                         followlinks=True):
            # Parse the local configuration file (if it exists)
            local_conf = Configuration()
            if '.DataTag.yaml' in files:
                local_conf.load(os.path.join(root, '.DataTag.yaml'))

            # Add all files, skipping hidden files and excluded ones
            for filename in files:
                if filename[0] == '.':
                    continue
                # Do we have to skip this file?
                skip = False
                for exclude in root_conf.exclude:
                    if fnmatch.fnmatchcase(filename, exclude):
                        print("%s [skip]" % (filename))
                        skip = True
                if skip:
                    continue

                path = os.path.join(root, filename)
                print(path)
                media = Media(path=path)
                media.save()
                for media_conf in local_conf.medias:
                    if fnmatch.fnmatchcase(filename, media_conf.pattern):
                        media.tags.add(*[tags[tag_name] for tag_name in media_conf.tags])
