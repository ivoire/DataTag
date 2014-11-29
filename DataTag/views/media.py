# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.http import Http404, HttpResponseForbidden, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from DataTag.models import Media
from DataTag.utils import mkdir

import mimetypes
import os
from PIL import Image


def media(request, path):
    pathname = os.path.join(settings.MEDIA_ROOT, path)
    # Get the Media and check the permissions
    media = get_object_or_404(Media, path=pathname)
    if not media.is_visible_to(request.user):
        return HttpResponseForbidden()

    # Get a thumbnails if requested
    size = request.GET.get('size', None)
    if size == 'small' or size == 'medium':
        smallpath = os.path.join(settings.CACHE_ROOT, size, path)
        if not os.path.isfile(smallpath):
            # Create the destination directory
            mkdir(os.path.dirname(smallpath))

            # Create the thumbnail, rotating if needed
            try:
                image = Image.open(pathname)
            except OSError:
                raise Http404
            exif = image._getexif()
            if exif:
                # Get orientation
                orientation = exif.get(0x0112, 0)
                if orientation == 3:
                    image = image.transpose(Image.ROTATE_180)
                elif orientation == 6:
                    image = image.transpose(Image.ROTATE_270)
                elif orientation == 8:
                    image = image.transpose(Image.ROTATE_90)

            if size == 'small':
                image.thumbnail((200, 200), Image.ANTIALIAS)
            else:
                image.thumbnail((800, 800), Image.ANTIALIAS)
            image.save(smallpath)

        pathname = smallpath

    # Stream the file
    wrapper = FileWrapper(open(pathname, 'rb'))
    mime = mimetypes.guess_type(pathname)
    response = StreamingHttpResponse(wrapper,
                                     content_type=mime[0] if mime[0]
                                     else 'text/plain')
    response['Content-Length'] = os.path.getsize(pathname)
    return response
