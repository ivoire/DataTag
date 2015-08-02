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

import yaml


class MediaConf(object):
    def __init__(self, pattern, tags, description):
        self.pattern = pattern
        self.tags = tags
        self.description = description


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
        self.default_groups = []

    def load(self, filename):
        try:
            with open(filename, 'r') as fin:
                y_conf = yaml.load(fin)
                for media in y_conf.get('medias', []):
                    pattern = media['pattern']
                    if not isinstance(pattern, list):
                        pattern = [pattern]
                    self.medias.append(MediaConf(pattern,
                                                 media.get('tags', []),
                                                 media.get('description', None)))
                for tag in y_conf.get('tags', []):
                    self.tags.append(TagConf(tag['name'],
                                             set(tag.get('groups', [])),
                                             tag.get('public', False),
                                             tag.get('root', False)))
                for exclude in y_conf.get('exclude', []):
                    self.exclude.append(exclude)
                for group_name in y_conf.get('defaults', {}).get('groups', []):
                    self.default_groups.append(group_name)
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
        medias = []
        tags = []

        # Create the list of media dicts
        for media in self.medias:
            new_media = {'pattern': media.pattern}
            if media.tags:
                new_media['tags'] = media.tags
            if media.description:
                new_media['description'] = media.description
            medias.append(new_media)

        # Create the list of tags dict
        for tag in self.tags:
            new_tag = {'name': tag.name}
            if tag.groups:
                new_tag['groups'] = list(tag.groups)
            if tag.public:
                new_tag['public'] = True
            if tag.root:
                new_tag['root'] = True
            tags.append(new_tag)

        # Create the final dict
        to_dump = {}
        if medias:
            to_dump['medias'] = medias
        if tags:
            to_dump['tags'] = tags
        if self.exclude:
            to_dump['exclude'] = self.exclude
        if self.default_groups:
            to_dump['defaults'] = dict()
            to_dump['defaults']['groups'] = self.default_groups

        with open(filename, 'w') as fout:
            yaml.dump(to_dump, fout,
                      default_flow_style=False, default_style=None, indent=1)
