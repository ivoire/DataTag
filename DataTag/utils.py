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

import errno
import json
import os
import subprocess


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
        out = subprocess.check_output(['exiftool', '-j', filename],
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
