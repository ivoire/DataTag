# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.conf.urls import include, patterns, url
from django.core.urlresolvers import reverse_lazy


# Main view
urlpatterns = patterns('DataTag.views.main',
    url(r'^$', 'index', name='index'),
)

# Authentication
urlpatterns += patterns('django.contrib.auth.views',
    url(r'^accounts/login/$', 'login', {'template_name': 'DataTag/account/login.html'}, name='accounts.login'),
    url(r'^accounts/logout/$', 'logout', {'template_name': 'DataTag/account/logged_out.html'}, name='accounts.logout'),
)

# Medias
urlpatterns += patterns('DataTag.views.media',
    url(r'^medias/(?P<path>.*$)', 'media', name='media'),
)

# Tags
urlpatterns += patterns('DataTag.views.tag',
    url(r'^tags/$', 'tag', {'path': ''}, name='tags.root'),
    url(r'^tags/(?P<path>.*)/$', 'tag', name='tags.details'),
    url(r'^(?P<path>.*)/$', 'browse', name='tags.browse'),
)
