# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from DataTag.models import Media, Tag

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
        tags_f = open(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'), 'r')
        tags_y = yaml.load(tags_f)
        for tag_name in tags_y.keys():
            print(" - %s" % (tag_name))
            Tag(name=tag_name).save()

        print("Adding the tag relationship")
        for tag_name in tags_y.keys():
            if not tags_y[tag_name]:
                continue

            tag = Tag.objects.get(name=tag_name)
            parent_name = tags_y[tag_name].get('parent', None)
            if parent_name:
                parent = Tag.objects.get(name=parent_name)
                tag.parent = parent
                tag.save()

        print("Importing the Media")
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            # Parse the local configuration file (if it exists)
            if '.DataTag.yaml' in files:
                conf_f = open(os.path.join(root, '.DataTag.yaml'), 'r')
                conf_y = yaml.load(conf_f)
            else:
                conf_y = dict()

            # Add all files
            for filename in files:
                if filename == '.DataTag.yaml':
                    continue
                path = os.path.join(root, filename)
                print path
                media = Media(path=path)
                media.save()
                for key in conf_y.keys():
                    if fnmatch.fnmatchcase(filename, key):
                        for tag_name in conf_y[key]['tags']:
                            tag = Tag.objects.get(name=tag_name)
                            media.tags.add(tag)
