# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Media, Tag


def index(request):
    return render_to_response('DataTag/main/index.html', {'tags': Tag.objects.all()},
                              context_instance=RequestContext(request))


def browse(request, path):
    medias = Media.objects.all()
    query_string = ''
    tags = []
    for tag_name in [p for p in path.split('/') if p]:
        query_string = query_string + '/' + tag_name
        tag = get_object_or_404(Tag, name=tag_name)
        tags.append({'obj': tag, 'path': query_string})
        medias = medias.filter(tags=tag)

    sub_tags = []
    for tag in Tag.objects.exclude(pk__in=[tag['obj'].pk for tag in tags]):
        count = medias.filter(tags=tag).count()
        if count:
            sub_tags.append({'obj': tag, 'count': count,
                             'path': query_string + '/' + tag.name})

    return render_to_response('DataTag/main/browse.html', {'tags': tags,
                                                           'sub_tags': sub_tags},
                              context_instance=RequestContext(request))
