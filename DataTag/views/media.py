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
import subprocess
from PIL import Image


def media(request, path):
    pathname = os.path.join(settings.MEDIA_ROOT, path)
    # Get the Media and check the permissions
    media = get_object_or_404(Media, path=pathname)
    if not media.is_visible_to(request.user):
        return HttpResponseForbidden()

    # Get a thumbnails if requested
    size_str = request.GET.get('size', None)
    if size_str == 'small' or size_str == 'medium':
        # Set the size
        if size_str == 'small':
            size = (280, 210)
        else:
            size = (800, 600)

        smallpath = os.path.join(settings.CACHE_ROOT, size_str, path)
        if not os.path.isfile(smallpath):
            # Create the destination directory
            mkdir(os.path.dirname(smallpath))

            # Detect the media format (image or video)
            try:
                image = Image.open(pathname)
                media_format = "image"
            except (OSError, IOError):
                media_format = "video"

            if media_format == "image":
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

                image.thumbnail(size, Image.ANTIALIAS)
                image.save(smallpath)

            elif media_format == "video":
                try:
                    subprocess.check_output(['ffmpeg', '-i', pathname,
                                             '-vcodec', 'mjpeg',
                                             '-vframes', '1',
                                             '-an', '-f', 'rawvideo',
                                             '-s', "%dx%d" % size,
                                             smallpath],
                                            stderr=subprocess.STDOUT)
                except Exception:
                    raise Http404

        pathname = smallpath

    # Stream the file
    wrapper = FileWrapper(open(pathname, 'rb'))
    mime = mimetypes.guess_type(pathname)
    response = StreamingHttpResponse(wrapper,
                                     content_type=mime[0] if mime[0]
                                     else 'text/plain')
    response['Content-Length'] = os.path.getsize(pathname)
    return response
