# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2015 Rémi Duraffort
# This file is part of DataTag.
#
# DataTag is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataTag is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with DataTag.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from django.core.servers.basehttp import FileWrapper
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import Http404, HttpResponseForbidden, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from DataTag.models import Media
from DataTag.utils import create_thumbnail, mkdir

import mimetypes
import os


def get_media(request, path):
    pathname = os.path.join(settings.MEDIA_ROOT, path)
    # Get the Media and check the permissions
    media = get_object_or_404(Media, path=pathname)
    if not media.is_visible_to(request.user):
        # If the user is not logged-in, redirect to the login page
        if not request.user.is_authenticated():
            return redirect_to_login(request.get_full_path(),
                                     settings.LOGIN_URL,
                                     REDIRECT_FIELD_NAME)
        else:
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
            # Create the destination directory and thumbnail
            mkdir(os.path.dirname(smallpath))
            if not create_thumbnail(media, smallpath, size):
                raise Http404
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
