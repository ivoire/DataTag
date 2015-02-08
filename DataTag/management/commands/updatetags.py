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

from DataTag.models import Media, Tag
from DataTag.config import Configuration
from DataTag.utils import load_exif

import fnmatch
import os


class Command(BaseCommand):
    args = None
    help = 'Update the tags'
    option_list = BaseCommand.option_list

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Removing old tags")
        Tag.objects.all().delete()

        self.stdout.write("Importing Tags...")
        root_conf = Configuration()
        root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))

        tags = {}
        for tag_conf in root_conf.tags:
            self.stdout.write(" - %s" % (tag_conf.name))
            tag = Tag(name=tag_conf.name, is_public=tag_conf.public,
                      is_root=tag_conf.root)
            tag.save()
            # Add groups
            if tag_conf.groups:
                group_list = tag_conf.groups
            else:
                group_list = root_conf.default_groups

            for group in group_list:
                self.stdout.write("   - %s" % (group))
                try:
                    tag.groups.add(Group.objects.get(name=group))
                except Group.DoesNotExist:
                    self.stderr.write("Group '%s' does not exists" % group)
                    return

            tags[tag_conf.name] = tag

        self.stdout.write("Updating the Media")
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

                # Add tags to file that matches
                try:
                    media = Media.objects.get(path=path)
                except Media.DoesNotExist:
                    self.stderr.write("Media '%s' does not exists" % path)
                    return

                for media_conf in local_conf.medias:
                    for pattern in media_conf.pattern:
                        if fnmatch.fnmatchcase(filename, pattern):
                            media.tags.add(*[tags[tag_name] for tag_name in media_conf.tags])
