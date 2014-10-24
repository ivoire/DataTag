# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Tag


def tag(request, tags):
    # TODO: check the permissions
    # Check the existence of the tags. Also check the parent relationship
    previous = None
    tag = None
    for tagname in tags.split('/'):
        tag = get_object_or_404(Tag, name=tagname, parent=tag)
        previous = tagname

    return render_to_response('DataTag/tag/index.html', {'tag': tag},
                              context_instance=RequestContext(request))
