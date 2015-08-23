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
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden, HttpResponseBadRequest, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from DataTag.models import Media, Tag
from DataTag.utils import mkdir

import os
import tarfile


def browse(request, path):
    # TODO: pagination !
    # Parse the 'path' and build the query
    medias = Media.objects.all()
    query_string = ''
    tags = []
    non_cat_tags = []
    cat_tags = []

    # Do we have to show everything ?
    all_tags = request.GET.get('all', False)

    # Skip too long requests
    path_elements = [p for p in path.split('/') if p]
    if len(path_elements) > settings.QUERY_MAX_LENGTH:
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
        tags.append({'obj': tag, 'path': query_string})
        medias = medias.filter(tags=tag)

    for tag in Tag.objects.exclude(pk__in=[tag['obj'].pk for tag in tags]).prefetch_related('groups').order_by('-name'):
        if not tag.is_visible_to(request.user):
            continue

        local_medias = medias.filter(tags=tag)
        count = local_medias.count()
        if count:
            obj = {'obj': tag, 'count': count,
                   'path': (query_string + '/' + tag.name),
                   'thumbnail': local_medias.order_by('?')[0]}

            # Is it a category ?
            if tag.category:
                cat_tags.append(obj)
            if all_tags or not tag.category:
                non_cat_tags.append(obj)

    # If their is not tags to show, redirect to tag details
    if not non_cat_tags and path:
        if cat_tags:
            return redirect(reverse('categories.browse') + "?path=%s" % path)
        else:
            return redirect(reverse('tags.details', args=[path]))


    return render_to_response('DataTag/tag/browse.html',
                              {'tags': tags, 'non_cat_tags': non_cat_tags,
                               'all_tags': all_tags},
                              context_instance=RequestContext(request))


# TODO: handle OR
def details(request, path):
    # Check that path is not empty. This should be forbidden by the url regular
    # expressions. But better to be safe than sorry.
    if path == '':
        return HttpResponseBadRequest()

    # Skip too long requests
    tag_name_list = [p for p in path.split('/') if p]
    if len(tag_name_list) > settings.QUERY_MAX_LENGTH:
        return HttpResponseBadRequest()

    # Check that all requested tags exists and are visible to the current user.
    tags = []
    medias = Media.objects.all()
    query_string = ''

    for tag_name in tag_name_list:
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
        tags.append({'obj': tag, 'path': query_string})

    # order by dates (from EXIF data)
    medias = medias.order_by('date')

    if 'download' in request.GET:
        # Too many elements
        # FIXME: should be a setting
        if len(medias) > 200:
            return HttpResponseForbidden()

        path = os.path.join(settings.CACHE_ROOT, 'downloads', *tag_name_list)
        path = path + '.tar'
        if not os.path.isfile(path):
            mkdir(os.path.dirname(path))
            with tarfile.open(path, 'w', dereference=True) as tar:
                index = 1
                for media in medias:
                    ext = os.path.splitext(media.path)[1]
                    tar.add(media.path, arcname="IMG_%04d%s" % (index, ext), recursive=False)
                    index += 1
        # Stream the file
        wrapper = FileWrapper(open(path, 'rb'))
        response = StreamingHttpResponse(wrapper,
                                         content_type='application/x-tar')
        response['Content-Length'] = os.path.getsize(path)
        # TODO: will not work correctly if tag contains double quotes
        response['Content-Disposition'] = "attachment; filename=\"%s\"" % os.path.basename(path)
        return response
    else:
        return render_to_response('DataTag/tag/details.html',
                                  {'medias': medias, 'tags': tags},
                                  context_instance=RequestContext(request))
