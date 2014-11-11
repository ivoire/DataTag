# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

import errno
import os
import yaml


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class MediaConf(object):
    def __init__(self, pattern, tags):
        self.pattern = pattern
        self.tags = tags


class TagConf(object):
    def __init__(self, name, groups, public):
        self.name = name
        self.groups = groups
        self.public = public


class Configuration:
    def __init__(self):
        self.medias = []
        self.tags = []

    def load(self, filename):
        try:
            with open(filename, 'r') as f:
                y = yaml.load(f)
                for media in y.get('medias', []):
                    self.medias.append(MediaConf(media['pattern'],
                                                 media['tags']))
                for tag in y.get('tags', []):
                    self.tags.append(TagConf(tag['name'],
                                             set(tag.get('groups', [])),
                                             tag.get('public', False)))
        except IOError:
            pass

    def media_tags(self):
        tags = set()
        for pattern in self.medias:
            tags.update(pattern.tags)
        return tags

    def tag_set(self):
        return set([tag.name for tag in self.tags])

    def dump(self, filename):
        # Transform into a dict of list of dicts
        medias = []
        tags = []
        for media in self.medias:
            medias.append({'pattern': media.pattern, 'tags': media.tags})
        for tag in self.tags:
            t = {'name': tag.name}
            if tag.groups:
                t['groups'] = list(tag.groups)
            if tag.public:
                t['public'] = True
            tags.append(t)
        with open(filename, 'w') as f:
            to_dump = {}
            if medias:
                to_dump['medias'] = medias
            if tags:
                to_dump['tags'] = tags
            yaml.dump(to_dump, f,
                      default_flow_style=False, default_style=None, indent=1)
