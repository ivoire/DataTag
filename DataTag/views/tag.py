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
from django.core.servers.basehttp import FileWrapper
from django.http import HttpResponseForbidden, HttpResponseBadRequest, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect, render_to_response
from django.template import RequestContext

from DataTag.models import Media, Tag
from DataTag.utils import mkdir

import os
import tarfile


def browse(request, path):
    # Parse the 'path' and build the query
    medias = Media.objects.all()
    query_string = ''
    tags = []
    root_tags = []
    non_root_tags = []
    sub_tags = []

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
            if tag.is_root:
                root_tags.insert(0, obj)
            else:
                non_root_tags.append(obj)
            sub_tags.append(obj)

    # If their is not tags to show, redirect to tag details
    if not root_tags and not non_root_tags:
        return redirect('tags.details', path=path)

    return render_to_response('DataTag/tag/browse.html',
                              {'tags': tags, 'root_tags': root_tags,
                               'non_root_tags': non_root_tags,
                               'sub_tags': sub_tags},
                              context_instance=RequestContext(request))


# TODO: handle OR
def details(request, path):
    # Check that path is not empty. This should be forbidden by the url regular
    # expressions. But better to be safe than sorry.
    if path == '':
        return HttpResponseBadRequest()

    # Skip too long requests
    tag_name_list = [p for p in path.split('/') if p]
    # TODO: should be a setting
    if len(tag_name_list) > 20:
        return HttpResponseBadRequest()

    # Check that all requested tags exists and are visible to the current user.
    tags = []
    medias = Media.objects.all()
    query_string = ''

    for tag_name in tag_name_list:
        query_string = query_string + '/' + tag_name
        tag = get_object_or_404(Tag, name=tag_name)
        if not tag.is_visible_to(request.user):
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
