# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Tag


def index(request):
    return render_to_response('DataTag/main/index.html', {'children': Tag.objects.filter(parent=None)},
                              context_instance=RequestContext(request))


def browse(request, path):
    previous = None
    tag = None
    for tagname in path.split('/'):
        tag = get_object_or_404(Tag, name=tagname, parent=tag)
        previous = tagname

    return render_to_response('DataTag/main/browse.html', {'tag': tag},
                              context_instance=RequestContext(request))
