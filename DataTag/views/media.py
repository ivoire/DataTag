# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.http import Http404, HttpResponseForbidden, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from DataTag.models import Media
from DataTag.utils import mkdir, keep_AR

import mimetypes
import os
import shutil
import subprocess
import tempfile
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
                # If the video size is known, compute the right size to keep
                # the A/R
                if medias.width != 0 and media.height != 0:
                    size = keep_AR((media.width, media.height), size)

                # Create the thumbnail in a temp directory in order to use the
                # use the right extensions for convert. In fact, convert uses
                # the extension to guess the input and output format. This is
                # not working for video thumbnails because we want to keep the
                # original filename (including the extension).
                tmp_dir = tempfile.mkdtemp('DataTag')
                tmp_path = os.path.join(tmp_dir, 'thumbnail.jpg')
                try:
                    subprocess.check_output(['ffmpeg', '-i', pathname,
                                             '-vcodec', 'mjpeg',
                                             '-vframes', '1',
                                             '-an', '-f', 'rawvideo',
                                             '-s', "%dx%d" % size,
                                             tmp_path],
                                            stderr=subprocess.STDOUT)
                    subprocess.check_output(['convert', tmp_path,
                                             os.path.join(settings.STATIC_ROOT,
                                                          'DataTag', 'img',
                                                          'overlay.png'),
                                             '-gravity', 'center', '-composite',
                                             '-format', 'jpg', '-quality', '90',
                                             tmp_path],
                                            stderr=subprocess.STDOUT)
                    # Move the file using shutil because the directories can be
                    # on different filesystems.
                    shutil.move(tmp_path, smallpath)
                except Exception:
                    raise Http404
                finally:
                    shutil.rmtree(tmp_dir)

        pathname = smallpath

    # Stream the file
    wrapper = FileWrapper(open(pathname, 'rb'))
    # FIXME: this will be wrong for video thumbnails
    mime = mimetypes.guess_type(pathname)
    response = StreamingHttpResponse(wrapper,
                                     content_type=mime[0] if mime[0]
                                     else 'text/plain')
    response['Content-Length'] = os.path.getsize(pathname)
    return response
