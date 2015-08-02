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

from django.conf import settings

import errno
import json
import os
from PIL import Image
import shutil
import subprocess
import tempfile


def mkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def load_exif(filename):
    try:
        out = subprocess.check_output(['exiftool', '-fast2', '-j', filename],
                                      stderr=subprocess.STDOUT,
                                      universal_newlines=True)
    except (OSError, subprocess.CalledProcessError):
        return {}

    try:
        exif = json.loads(out)
    except (TypeError, ValueError):
        return {}

    return exif[0]


def keep_AR(old_size, new_size):
    x, y = old_size
    if x > new_size[0]:
        y = int(max(y * new_size[0] / x, 1))
        x = int(new_size[0])
    if y > new_size[1]:
        x = int(max(x * new_size[1] / y, 1))
        y = int(new_size[1])
    return (x, y)


def create_thumbnail(media, dest_path, size):
    src_path = media.path
    # Detect the media format (image or video)
    try:
        image = Image.open(src_path)
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
        image.save(dest_path)

    elif media_format == "video":
        # If the video size is known, compute the right size to keep
        # the A/R
        if media.width != 0 and media.height != 0:
            size = keep_AR((media.width, media.height), size)

        # Create the thumbnail in a temp directory in order to use the
        # use the right extensions for convert. In fact, convert uses
        # the extension to guess the input and output format. This is
        # not working for video thumbnails because we want to keep the
        # original filename (including the extension).
        tmp_dir = tempfile.mkdtemp('DataTag')
        tmp_path = os.path.join(tmp_dir, 'thumbnail.jpg')
        try:
            subprocess.check_output(['ffmpeg', '-i', src_path,
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
            shutil.move(tmp_path, dest_path)
        except Exception:
            return False
        finally:
            shutil.rmtree(tmp_dir)
    return True
