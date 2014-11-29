# -*- coding: utf-8 -*-
# vim: set ts=4

from django.contrib.messages import constants as message_constants


# Accounts related urls
LOGIN_URL = 'accounts.login'
LOGOUT_UR = 'accounts.logout'
LOGIN_REDIRECT_URL = 'accounts.profile'

# For bootstrap 3, error messages should be flaged 'danger'
MESSAGE_TAGS = {
    message_constants.ERROR: 'danger'
}
