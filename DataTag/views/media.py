# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template import RequestContext

from DataTag.models import Media
from DataTag.utils import mkdir

import mimetypes
import os
from PIL import Image


def media(request, path):
    pathname = os.path.join(settings.MEDIA_ROOT, path)
    # Get the Media and check the permissions
    media = get_object_or_404(Media, path=pathname)
    # TODO: check the permissions

    # Get a thumbnails if requested
    size = request.GET.get('size', None)
    if size == 'small':
        smallpath = os.path.join(settings.CACHE_ROOT, 'small', path)
        if not os.path.isfile(smallpath):
        # Create the destination directory
            mkdir(os.path.dirname(smallpath))

            # Create the thumbnail, copying the EXIF data
            image = Image.open(pathname)
            # TODO: what if there is no EXIF data?
            # http://stackoverflow.com/questions/4228530/pil-thumbnail-is-rotating-my-image
            exif = image.info['exif']
            image.thumbnail((200,200), Image.ANTIALIAS)
            image.save(smallpath, exif=exif)
        pathname = smallpath

    # Stream the file
    wrapper = FileWrapper(open(pathname))
    mime = mimetypes.guess_type(pathname)
    response = HttpResponse(wrapper,
                            content_type=mime[0] if mime[0] else 'text/plain')
    response['Content-Length'] = os.path.getsize(pathname)
    return response
