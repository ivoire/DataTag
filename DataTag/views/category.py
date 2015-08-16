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

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Category, Media, Tag


def details(request, name):
    # TODO; add optional path
    category = get_object_or_404(Category, name=name)

    # Grab all tags with this category
    tags = []
    for tag in Tag.objects.filter(category=category):
        if not tag.is_visible_to(request.user):
            continue

        medias = Media.objects.filter(tags=tag)
        count = medias.count()
        if count:
            obj = {'obj': tag, 'count': count,
                   'path': '/' + tag.name,
                   'thumbnail': medias.order_by('?')[0]}
            tags.append(obj)

    return render_to_response('DataTag/category/details.html',
                              {'category': category,
                               'tags': tags},
                              context_instance=RequestContext(request))
