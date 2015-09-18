# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2015 Rémi Duraffort
# This file is part of DataTag.
#
# DataTag is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataTag is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with DataTag.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from django.db import transaction
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.utils import timezone

from DataTag.models import Category, Media, Tag
from DataTag.config import Configuration
from DataTag.utils import load_exif

import datetime
import fnmatch
import os
import pytz


class Command(BaseCommand):
    args = None
    help = 'Synchronize the file system with the database'
    option_list = BaseCommand.option_list

    def create_tag(self, tag_conf, root_conf, categories):
        tag = Tag(name=tag_conf.name, description=tag_conf.description,
                  shortname=tag_conf.shortname,
                  category=categories[tag_conf.category],
                  is_public=tag_conf.public)
        tag.save()

        # Add groups
        if tag_conf.groups:
            group_list = tag_conf.groups
        else:
            group_list = root_conf.default_groups

        for group in group_list:
            self.stdout.write("   - %s" % (group))
            tag.groups.add(Group.objects.get(name=group))

        return tag

    @transaction.atomic
    def handle(self, *args, **kwargs):
        # Are we importing all medias or only a sub-directory
        if len(args) > 0:
            base_dirs = args
            root_conf = Configuration()
            root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))
            tags = {}
            # TODO: add missing categories
            self.stdout.write("Importing new tags if needed")
            for tag_name in root_conf.tags:
                tag_conf = root_conf.tags[tag_name]
                try:
                    tag = Tag.objects.get(name=tag_conf.name)
                except Tag.DoesNotExist:
                    self.stdout.write(" - %s" % (tag_conf.name))
                    tag = self.create_tag(tag_conf, root_conf, categories)
                tags[tag_conf.name] = tag
        else:
            self.stdout.write("Removing old data")
            base_dirs = [settings.MEDIA_ROOT]
            Category.objects.all().delete()
            Media.objects.all().delete()
            Tag.objects.all().delete()

            self.stdout.write("Loading root configuration")
            root_conf = Configuration()
            root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))

            self.stdout.write("Importing Categories...")
            # Create the dictionnay with a None key. This allows to have the same
            # code when a tag does not have any category.
            categories = {None: None}
            for category_name in root_conf.categories:
                current_category = root_conf.categories[category_name]
                self.stdout.write(" - %s" % (category_name))
                cat = Category(name=current_category.name,
                               description=current_category.description)
                cat.save()
                # Keep all loaded category objects
                categories[category_name] = cat

            self.stdout.write("Importing Tags...")
            # Load all the tags
            tags = {}
            for tag_name in root_conf.tags:
                tag_conf = root_conf.tags[tag_name]
                self.stdout.write(" - %s" % (tag_conf.name))
                tags[tag_conf.name] = self.create_tag(tag_conf, root_conf, categories)

        # TODO: add a specific option for this
        tz = pytz.timezone(settings.TIME_ZONE)
        self.stdout.write("Importing the Media")
        for base_dir in base_dirs:
            # TODO: check that it's a subdirectory of settings.MEDIA_ROOT
            base_dir = os.path.abspath(base_dir)
            self.stdout.write("From '%s'" % base_dir)
            for root, _, files in os.walk(base_dir,
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
                    date_key = None
                    if 'DateTimeOriginal' in exif:
                        date_key = 'DateTimeOriginal'
                    elif 'MediaCreateDate' in exif:
                        date_key = 'MediaCreateDate'

                    if date_key is not None:
                        try:
                            date = datetime.datetime.strptime(exif[date_key],
                                                              "%Y:%m:%d %H:%M:%S")
                            date = tz.localize(date)
                        except ValueError:
                            # TODO: handle date with timezone like 2014:05:09 19:32:29.92+02:00
                            self.stdout.write(" => invalid date (%s)" % exif[date_key])
                    else:
                        self.stdout.write(" => no date found")
                    media = Media(path=path, date=date,
                                  width=exif.get('ImageWidth', 0),
                                  height=exif.get('ImageHeight', 0))
                    media.save()
                    for media_conf in local_conf.medias:
                        for pattern in media_conf.pattern:
                            if fnmatch.fnmatchcase(filename, pattern):
                                if media_conf.tags:
                                    media.tags.add(*[tags[tag_name] for tag_name in media_conf.tags])
                                if media_conf.description:
                                    media.description = media_conf.description
                                    media.save()
