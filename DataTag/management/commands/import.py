# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from DataTag.models import Media, Tag
from DataTag.utils import Configuration

import datetime
import fnmatch
import os
from PIL import Image
import pytz


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
        # TODO: add a specific option for this
        tz = pytz.timezone(settings.TIME_ZONE)
        for tag_conf in root_conf.tags:
            print(" - %s" % (tag_conf.name))
            tag = Tag(name=tag_conf.name, is_public=tag_conf.public,
                      is_root=tag_conf.root)
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
                date = timezone.now()
                try:
                    image = Image.open(path)
                    # TODO: read more metada using something like readexif
                    if hasattr(image, '_getexif') and image._getexif() is not None:
                        exif_date = image._getexif().get(0x9003, u'0000:00:00 00:00:00')
                        if exif_date != u'0000:00:00 00:00:00':
                            date = datetime.datetime.strptime(exif_date,
                                                              "%Y:%m:%d %H:%M:%S")
                            date = tz.localize(date)
                except (OSError, IOError):
                    # TODO: do a stat to get the last modified date
                    pass
                print(path)
                media = Media(path=path, date=date)
                media.save()
                for media_conf in local_conf.medias:
                    if fnmatch.fnmatchcase(filename, media_conf.pattern):
                        media.tags.add(*[tags[tag_name] for tag_name in media_conf.tags])
