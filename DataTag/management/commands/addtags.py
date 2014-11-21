# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from DataTag.utils import Configuration, MediaConf

from optparse import make_option


class Command(BaseCommand):
    args = None
    help = 'Collect the tags from the sub-directories'
    option_list = BaseCommand.option_list + (
        make_option('-p', '--pattern',
                    dest='pattern',
                    help='Pattern when matching the files',
                    default='*'),
    )

    def handle(self, *args, **kwargs):
        pattern = kwargs['pattern']
        new_tags = set(args)

        # Load the tags from the configuration
        local_conf = Configuration()
        local_conf.load('.DataTag.yaml')

        # Look for the pattern
        pattern_found = False
        for media in local_conf.medias:
            if media.pattern == pattern:
                pattern_found = True

        if pattern_found:
            media.tags = list(set(media.tags) | new_tags)
        else:
            local_conf.medias.append(MediaConf(pattern, list(new_tags)))

        local_conf.dump(".DataTag.yaml")
