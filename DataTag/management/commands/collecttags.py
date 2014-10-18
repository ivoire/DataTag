# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

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
                with open(os.path.join(root, '.DataTag.yaml'), 'r') as local_conf:
                    local_conf = yaml.load(local_conf)
                    for key in local_conf:
                        for tag in local_conf[key]['tags']:
                            used_tags.add(tag)

        # Load the tags from the root configuration
        root_tags = set()
        try:
            with open(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'), 'r') as root_conf:
                root_conf = yaml.load(root_conf)
                for tag in root_conf:
                    root_tags.add(tag)
        except IOError:
            pass

        # Add the tags that are missing in the root_tags
        missing_tags = used_tags - root_tags
        if missing_tags:
            print("Adding missing tags")
            print("===================")
            with open(os.path.join(settings.MEDIA_ROOT, '.DataTag.yaml'), 'a+') as root_conf:
                for tag in missing_tags:
                    print(" - %s" % (tag))
                    root_conf.write("%s:\n" % (tag))
        else:
            print("No missing tags")
