# -*- coding: utf-8 -*-
# vim: set ts=

from __future__ import unicode_literals

from django.conf import settings
from django.core.management.base import BaseCommand

from optparse import make_option
import yaml


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
        local_tags = set()
        pattern_in_local = False
        try:
            with open('.DataTag.yaml', 'r') as local_conf:
                local_conf = yaml.load(local_conf)
                if pattern in local_conf:
                    pattern_in_local = True
                    for tag in local_conf[pattern]['tags']:
                        local_tags.add(tag)
        except IOError:
            print 'no such file or directory'
            pass

        # Add the tags that are missing in the configuration
        missing_tags = new_tags - local_tags
        if missing_tags:
            print("Adding missing tags")
            print("===================")

            if pattern_in_local:
                print "TODO"
            else:
                with open('.DataTag.yaml', 'a+') as local_conf:
                    if '*' in pattern or ':' in pattern:
                        local_conf.write("'%s':\n    tags:\n" % (pattern))
                    else:
                        local_conf.write("%s:\n    tags:\n" % (pattern))
                    for tag in missing_tags:
                        print(" - %s" % (tag))
                        local_conf.write("        - %s\n" % (tag))
        else:
            print("No missing tags")
