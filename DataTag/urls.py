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

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy

from DataTag.views.account import DTAuthenticationForm, DTPasswordChangeForm

# Main view
urlpatterns = patterns('DataTag.views.main',
    url(r'^$', 'index', name='index'),
)

# Authentication
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/$', 'login', {'template_name': 'DataTag/account/login.html', 'authentication_form': DTAuthenticationForm}, name='accounts.login'),
    url(r'^accounts/logout/$', 'logout', {'template_name': 'DataTag/account/logged_out.html'}, name='accounts.logout'),
    url(r'^accounts/password/change/$', 'password_change', {'template_name': 'DataTag/account/password_change.html', 'password_change_form': DTPasswordChangeForm, 'post_change_redirect': reverse_lazy('accounts.password_change_done')}, name='accounts.password_change'),
)

# Account
urlpatterns += patterns('DataTag.views.account',
    url(r'^accounts/register/$', 'register', name='accounts.register'),
    url(r'^accounts/profile/$', 'profile', name='accounts.profile'),
    url(r'^accounts/profile/update/$', 'update', name='accounts.profile.update'),
    url(r'^accounts/password/change/done/$', 'password_change_done', name='accounts.password_change_done'),
)

# Medias
urlpatterns += patterns('DataTag.views.media',
    url(r'^medias/(?P<path>.*$)', 'media', name='media'),
)

# Tags
urlpatterns += patterns('DataTag.views.tag',
    url(r'^tags/$', 'details', {'path': ''}, name='tags.root'),
    url(r'^tags(?P<path>/.*)/$', 'details', name='tags.details'),
    url(r'^browse/$', 'browse', {'path': ''}, name='tags.browse.root'),
    url(r'^browse(?P<path>/.*)/$', 'browse', name='tags.browse'),
)
