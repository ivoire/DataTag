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

from django.conf.urls import url
from django.contrib.auth import views as v_auth
from django.core.urlresolvers import reverse_lazy

from DataTag.views import account as v_account
from DataTag.views import category as v_category
from DataTag.views import main as v_main
from DataTag.views import media as v_media
from DataTag.views import tag as v_tag
from DataTag.views.account import DTAuthenticationForm, DTPasswordChangeForm

urlpatterns = [
    # Main view
    url(r'^$', v_main.index, name='index'),

    # Authentication
    url(r'^accounts/login/$', v_auth.login, {'template_name': 'DataTag/account/login.html', 'authentication_form': DTAuthenticationForm}, name='accounts.login'),
    url(r'^accounts/logout/$', v_auth.logout, {'template_name': 'DataTag/account/logged_out.html'}, name='accounts.logout'),
    url(r'^accounts/password/change/$', v_auth.password_change, {'template_name': 'DataTag/account/password_change.html', 'password_change_form': DTPasswordChangeForm, 'post_change_redirect': reverse_lazy('accounts.password_change_done')}, name='accounts.password_change'),

    # Account
    url(r'^accounts/register/$', v_account.register, name='accounts.register'),
    url(r'^accounts/profile/$', v_account.profile, name='accounts.profile'),
    url(r'^accounts/profile/update/$', v_account.update, name='accounts.profile.update'),
    url(r'^accounts/password/change/done/$', v_account.password_change_done, name='accounts.password_change_done'),

    # Medias
    url(r'^medias/(?P<path>.*$)', v_media.get_media, name='media'),

    # Tags
    url(r'^tags(?P<path>/.+)/$', v_tag.details, name='tags.details'),
    url(r'^browse/$', v_tag.browse, {'path': ''}, name='tags.browse.root'),
    url(r'^browse(?P<path>/.*)/$', v_tag.browse, name='tags.browse'),

    # Categories
    url(r'^categories/(?P<name>[^/]+)/$', v_category.details, {'path': ''}, name='categories.details.root'),
    url(r'^categories/(?P<name>[^/]+)(?P<path>/.*)/$', v_category.details, name='categories.details'),
]
