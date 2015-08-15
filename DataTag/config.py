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


class CategoryConf(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description


class MediaConf(object):
    def __init__(self, pattern, tags, description):
        self.pattern = pattern
        self.tags = tags
        self.description = description


class TagConf(object):
    def __init__(self, name, description, groups, category, public, root):
        self.name = name
        self.description = description
        self.groups = groups
        self.category = category
        self.public = public
        self.root = root


class Configuration(object):
    def __init__(self):
        self.medias = []
        self.tags = {}
        self.categories = {}
        self.exclude = []
        self.default_groups = []

    def load(self, filename):
        try:
            # Load the configuration file
            with open(filename, 'r') as fin:
                y_conf = yaml.load(fin)

                # Load the medias
                for media in y_conf.get('medias', []):
                    pattern = media['pattern']
                    if not isinstance(pattern, list):
                        pattern = [pattern]
                    self.medias.append(MediaConf(pattern,
                                                 media.get('tags', []),
                                                 media.get('description', None)))
                # Load the tags
                tags = y_conf.get('tags', {})
                for tag_name in tags:
                    tag = tags[tag_name]
                    self.tags[tag_name] = TagConf(tag_name,
                                                  tag.get('description', None),
                                                  set(tag.get('groups', [])),
                                                  tag.get('category', None),
                                                  tag.get('public', False),
                                                  tag.get('root', False))
                # Load categories
                categories = y_conf.get('categories', {})
                for category_name in categories:
                    category = categories[category_name]
                    self.categories[category_name] = CategoryConf(
                                                        category_name,
                                                        category.get('description', None))
                # Load excludes and default groups
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
        return set(self.tags.keys())

    def dump(self, filename):
        medias = []
        tags = {}

        # Create the list of media dicts
        for media in self.medias:
            new_media = {'pattern': media.pattern}
            if media.tags:
                new_media['tags'] = media.tags
            if media.description:
                new_media['description'] = media.description
            medias.append(new_media)

        # Create the list of tags dict
        for tag_name in self.tags:
            tag = self.tags[tag_name]
            tags[tag.name] = {}

            if tag.description:
                tags[tag.name]['description'] = tag.description
            if tag.groups:
                tags[tag.name]['groups'] = list(tag.groups)
            if tag.category:
                tags[tag.name]['category'] = tag.category
            if tag.public:
                tags[tag.name]['public'] = True
            if tag.root:
                tags[tag.name]['root'] = True

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

        # TODO: dump the categories

        with open(filename, 'w') as fout:
            yaml.dump(to_dump, fout,
                      default_flow_style=False, default_style=None, indent=1)
