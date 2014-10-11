# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from DataTag.models import Media

import mimetypes
import os


def media(request, path):
    # Get the Media and check the permissions
    media = get_object_or_404(Media, path=os.path.join(settings.MEDIA_ROOT,
                                                       path))
    # TODO: check the permissions

    # Stream the file
    wrapper = FileWrapper(open(media.path))
    mime = mimetypes.guess_type(media.path)
    response = HttpResponse(wrapper,
                            content_type=mime[0] if mime[0] else 'text/plain')
    response['Content-Length'] = os.path.getsize(media.path)
    return response
