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

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible

import os


@python_2_unicode_compatible
class Media(models.Model):
    tags = models.ManyToManyField('Tag', blank=True)
    path = models.FilePathField(path=settings.MEDIA_ROOT, recursive=True,
                                max_length=256, db_index=True)
    width = models.IntegerField()
    height = models.IntegerField()
    date = models.DateTimeField()
    description = models.CharField(max_length=256, blank=True, null=True)

    def __str__(self):
        base_length = len(settings.MEDIA_ROOT)
        return "%s" % (self.path[base_length+1:])

    def get_absolute_url(self):
        base_length = len(settings.MEDIA_ROOT)
        return reverse('media', args=[self.path[base_length+1:]])

    def is_visible_to(self, user):
        """
        Return true if this medias is visible for the given user
        """
        # Is the user anonymous?
        if user.is_anonymous():
            if self.tags.filter(is_public=True).exists():
                return True
        else:
            user_groups_set = set(user.groups.all())
            tags = self.tags.all()
            for tag in tags:
                if tag.is_public:
                    return True
                tag_groups_set = set(tag.groups.all())
                # A tag without groups is visible to all authenticated users
                if not tag_groups_set:
                    return True
                if tag_groups_set & user_groups_set:
                    return True
            # A media without tags is visible to all authenticated users
            if not tags:
                return True
        return False

    def basename(self):
        return os.path.basename(self.path)


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=128, db_index=True, unique=True)
    description = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        return "%s" % (self.name)


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=128, db_index=True, unique=True)
    description = models.CharField(max_length=1024, blank=True, null=True)
    groups = models.ManyToManyField(Group, blank=True)
    category = models.ForeignKey(Category, blank=True, null=True, default=None)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('tags.details', args=['/' + self.name])

    def is_visible_to(self, user):
        """
        Return True if this tag is visible to the given user
        """
        if self.is_public:
            return True
        if user.is_anonymous():
            return False

        tag_groups_set = set(self.groups.all())
        if not tag_groups_set:
            return True
        user_groups_set = set(user.groups.all())
        if tag_groups_set & user_groups_set:
            return True
        return False
