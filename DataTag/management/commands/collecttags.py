# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from DataTag.utils import Configuration, TagConf
import os
import yaml


class Command(BaseCommand):
    args = None
    help = 'Collect the tags from the sub-directories'
    option_list = BaseCommand.option_list

    def handle(self, *args, **kwargs):
        # Find the new tags
        used_tags = set()
        for root, dirs, files in os.walk(settings.MEDIA_ROOT, followlinks=True):
            # Skip the root configuration file
            if root == settings.MEDIA_ROOT:
                continue

            # Parse the local configuration file
            if '.DataTag.yaml' in files:
                local_conf = Configuration()
                local_conf.load(os.path.join(root, '.DataTag.yaml'))
                used_tags.update(local_conf.media_tags())

        # Load the tags from the root configuration
        root_conf = Configuration()
        root_conf.load(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))

        # Add the tags that are missing in the root_tags
        missing_tags = used_tags - root_conf.tag_set()
        if missing_tags:
            print("Adding missing tags")
            print("===================")
            for tag in missing_tags:
                print(" - %s" % (tag))
                root_conf.tags.append(TagConf(tag, set()))
            root_conf.dump(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))
        else:
            print("No missing tags")
