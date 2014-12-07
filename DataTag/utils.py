# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

import errno
import os
import yaml


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class MediaConf(object):
    def __init__(self, pattern, tags):
        self.pattern = pattern
        self.tags = tags


class TagConf(object):
    def __init__(self, name, groups, public, root):
        self.name = name
        self.groups = groups
        self.public = public
        self.root = root


class Configuration(object):
    def __init__(self):
        self.medias = []
        self.tags = []
        self.exclude = []

    def load(self, filename):
        try:
            with open(filename, 'r') as fin:
                y_conf = yaml.load(fin)
                for media in y_conf.get('medias', []):
                    self.medias.append(MediaConf(media['pattern'],
                                                 media['tags']))
                for tag in y_conf.get('tags', []):
                    self.tags.append(TagConf(tag['name'],
                                             set(tag.get('groups', [])),
                                             tag.get('public', False),
                                             tag.get('root', False)))
                for exclude in y_conf.get('exclude', []):
                    self.exclude.append(exclude)
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
            new_tag = {'name': tag.name}
            if tag.groups:
                new_tag['groups'] = list(tag.groups)
            if tag.public:
                new_tag['public'] = True
            if tag.root:
                new_tag['root'] = True
            tags.append(new_tag)
        with open(filename, 'w') as fout:
            to_dump = {}
            if medias:
                to_dump['medias'] = medias
            if tags:
                to_dump['tags'] = tags
            if self.exclude:
                to_dump['exclude'] = self.exclude
            yaml.dump(to_dump, fout,
                      default_flow_style=False, default_style=None, indent=1)
