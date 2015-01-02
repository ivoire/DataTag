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
from django.contrib import admin

from DataTag.models import Media, Tag


class MediaAdmin(admin.ModelAdmin):
    list_display = ('path_short', 'tag_list', 'size', 'date')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    search_fields = ('path',)

    def path_short(self, obj):
        return obj.path[len(settings.MEDIA_ROOT)+1:]

    def size(self, obj):
        return "%dx%d" % (obj.width, obj.height)

    def tag_list(self, obj):
        return "|".join([tag.name for tag in obj.tags.all()])


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_list', 'is_public', 'is_root')
    list_filter = ('groups',)
    filter_horizontal = ('groups',)

    def group_list(self, obj):
        return "|".join([tag.name for tag in obj.groups.all()])

admin.site.register(Media, MediaAdmin)
admin.site.register(Tag, TagAdmin)
