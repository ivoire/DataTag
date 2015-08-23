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

from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Category, Media, Tag

import random


def browse(request):
    # Handle query strings
    path = request.GET.get('path', '')
    medias = Media.objects.all()
    if path:
        # Parse the 'path' and build the query
        query_string = ''
        path_elements = [p for p in path.split('/') if p]
        # TODO:should be a setting
        if len(path_elements) > 20:
            return HttpResponseBadRequest()

        # Show only the selected tags
        for tag_name in path_elements:
            query_string = query_string + '/' + tag_name
            tag = get_object_or_404(Tag, name=tag_name)
            if not tag.is_visible_to(request.user):
                # If the user is not logged-in, redirect to the login page
                if not request.user.is_authenticated():
                    return redirect_to_login(request.get_full_path(),
                                             settings.LOGIN_URL,
                                             REDIRECT_FIELD_NAME)
                else:
                    return HttpResponseForbidden()
            medias = medias.filter(tags=tag)

    # List all available categories
    cats = Category.objects.all().order_by('name')
    categories = []

    # For each category, filter for the current user
    for cat in cats:
        tags = Tag.objects.filter(category=cat)
        available_tags = []
        count = 0
        for tag in tags:
            if tag.is_visible_to(request.user):
                if medias.filter(tags=tag).count():
                    available_tags.append(tag)
                    count += 1
        if not available_tags:
            continue

        # Get a random tag for the thumbnail
        tag = random.choice(available_tags)
        obj = {'obj': cat, 'count': count,
               'path': path, 'thumbnail': Media.objects.filter(tags=tag).order_by('?')[0]}
        categories.append(obj)

    return render_to_response('DataTag/category/browse.html',
                              {'categories': categories},
                              context_instance=RequestContext(request))


def details(request, name, path):
    category = get_object_or_404(Category, name=name)

    # Parse the 'path' and build the query
    medias = Media.objects.all()
    query_string = ''

    # Skip too long requests
    # TODO: should be a setting
    path_elements = [p for p in path.split('/') if p]
    if len(path_elements) > 20:
        return HttpResponseBadRequest()

    # Show only the selected tags
    for tag_name in path_elements:
        query_string = query_string + '/' + tag_name
        tag = get_object_or_404(Tag, name=tag_name)
        if not tag.is_visible_to(request.user):
            # If the user is not logged-in, redirect to the login page
            if not request.user.is_authenticated():
                return redirect_to_login(request.get_full_path(),
                                         settings.LOGIN_URL,
                                         REDIRECT_FIELD_NAME)
            else:
                return HttpResponseForbidden()
        medias = medias.filter(tags=tag)

    # Grab all tags with this category
    tags = []
    for tag in Tag.objects.filter(category=category).order_by('name'):
        if not tag.is_visible_to(request.user):
            continue

        local_medias = medias.filter(tags=tag)
        count = local_medias.count()
        if count:
            obj = {'obj': tag, 'count': count,
                   'path': (query_string + '/' + tag.name),
                   'thumbnail': local_medias.order_by('?')[0]}
            tags.append(obj)

    return render_to_response('DataTag/category/details.html',
                              {'category': category,
                               'tags': tags},
                              context_instance=RequestContext(request))
