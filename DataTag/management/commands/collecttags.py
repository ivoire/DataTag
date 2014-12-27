# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from DataTag.utils import Configuration, TagConf
import os


class Command(BaseCommand):
    args = None
    help = 'Collect the tags from the sub-directories'
    option_list = BaseCommand.option_list

    def handle(self, *args, **kwargs):
        # Find the new tags
        used_tags = set()
        for root, _, files in os.walk(settings.MEDIA_ROOT,
                                      followlinks=True):
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
            self.stdout.write("Adding missing tags")
            self.stdout.write("===================")
            for tag in missing_tags:
                self.stdout.write(" - %s" % (tag))
                root_conf.tags.append(TagConf(tag, set(), False, False))
            root_conf.dump(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'))
        else:
            self.stdout.write("No missing tags")
