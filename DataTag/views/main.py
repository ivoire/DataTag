# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Media, Tag


def index(request):
    tags = []
    for tag in Tag.objects.all():
        medias = Media.objects.filter(tags=tag)
        if medias.exists():
            tags.append({'obj': tag, 'count': medias.count(),
                         'path': tag.name,
                         'thumbnail': medias.order_by('?')[0]})
    return render_to_response('DataTag/main/index.html', {'tags': tags},
                              context_instance=RequestContext(request))
