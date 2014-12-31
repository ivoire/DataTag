# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from DataTag.models import Media, Tag
from DataTag.utils import Configuration, load_exif

import datetime
import fnmatch
import os
import pytz


class Command(BaseCommand):
    args = None
    help = 'Synchronize the file system with the database'
    option_list = BaseCommand.option_list

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Removing old data")
        Media.objects.all().delete()
        Tag.objects.all().delete()

        self.stdout.write("Importing Tags...")
        root_conf = Configuration()
        root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))

        tags = {}
        # TODO: add a specific option for this
        tz = pytz.timezone(settings.TIME_ZONE)
        for tag_conf in root_conf.tags:
            self.stdout.write(" - %s" % (tag_conf.name))
            tag = Tag(name=tag_conf.name, is_public=tag_conf.public,
                      is_root=tag_conf.root)
            tag.save()
            # Add groups
            for group in tag_conf.groups:
                self.stdout.write("   - %s" % (group))
                tag.groups.add(Group.objects.get(name=group))

            tags[tag_conf.name] = tag

        self.stdout.write("Importing the Media")
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
                        self.stdout.write("%s [skip]\n" % (filename))
                        skip = True
                if skip:
                    continue

                path = os.path.join(root, filename)
                self.stdout.write("%s" % path)

                # Read EXIF data
                date = timezone.now()
                exif = load_exif(path)
                if 'DateTimeOriginal' in exif:
                    try:
                        date = datetime.datetime.strptime(exif['DateTimeOriginal'],
                                                          "%Y:%m:%d %H:%M:%S")
                        date = tz.localize(date)
                    except ValueError:
                        self.stdout.write(" => invalid date (%s)" % exif['DateTimeOriginal'])
                else:
                    self.stdout.write(" => no date found")
                media = Media(path=path, date=date,
                              width=exif.get('ImageWidth', 0),
                              height=exif.get('ImageHeight', 0))
                media.save()
                for media_conf in local_conf.medias:
                    if fnmatch.fnmatchcase(filename, media_conf.pattern):
                        media.tags.add(*[tags[tag_name] for tag_name in media_conf.tags])
