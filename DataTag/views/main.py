# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from DataTag.models import Media, Tag


def index(request):
    return render_to_response('DataTag/main/index.html',
                              context_instance=RequestContext(request))
