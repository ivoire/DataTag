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

from django.contrib.messages import constants as message_constants

# Accounts related urls
LOGIN_URL = 'accounts.login'
LOGOUT_UR = 'accounts.logout'
LOGIN_REDIRECT_URL = 'accounts.profile'

# For bootstrap 3, error messages should be flaged 'danger'
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger'
}

# Choose between avconv and ffmpeg
VIDEO_CMD = "ffmpeg"

# The maximum depth of query string
QUERY_MAX_LENGTH = 20
