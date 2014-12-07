# -*- coding: utf-8 -*-
# vim: set ts=4

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
