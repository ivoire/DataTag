# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Media, Tag


def browse(request, path):
    # Parse the 'path' and build the query
    medias = Media.objects.all()
    query_string = ''
    tags = []
    for tag_name in [p for p in path.split('/') if p]:
        query_string = query_string + '/' + tag_name
        tag = get_object_or_404(Tag, name=tag_name)
        if not tag.is_visible_to(request.user):
            return HttpResponseForbidden()
        tags.append({'obj': tag, 'path': query_string})
        medias = medias.filter(tags=tag)

    sub_tags = []
    for tag in Tag.objects.exclude(pk__in=[tag['obj'].pk for tag in tags]).order_by('-name'):
        if not tag.is_visible_to(request.user):
            continue
        local_medias = medias.filter(tags=tag)
        count = local_medias.count()
        if count:
            sub_tags.append({'obj': tag, 'count': count,
                             'path': (query_string + '/' + tag.name),
                             'thumbnail': local_medias.order_by('?')[0]})

    return render_to_response('DataTag/tag/browse.html',
                              {'tags': tags, 'sub_tags': sub_tags},
                              context_instance=RequestContext(request))


def details(request, path):
    # TODO: handle OR
    # Check the existence of all tags
    tags = []
    medias = Media.objects.all()
    query_string = ''
    for tag_name in [p for p in path.split('/') if p]:
        query_string = query_string + '/' + tag_name
        tag = get_object_or_404(Tag, name=tag_name)
        if not tag.is_visible_to(request.user):
            return HttpResponseForbidden()
        medias = medias.filter(tags=tag)
        tags.append({'obj': tag, 'path': query_string})

    # TODO: order by dates (from EXIF data)
    medias = medias.order_by('path')

    # Special case for '' path. In this case medias are not filtered
    if path == '':
        medias = [m for m in medias if m.is_visible_to(request.user)]

    return render_to_response('DataTag/tag/details.html',
                              {'medias': medias, 'tags': tags},
                              context_instance=RequestContext(request))
