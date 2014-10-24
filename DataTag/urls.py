# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.conf.urls import include, patterns, url
from django.core.urlresolvers import reverse_lazy


urlpatterns = patterns('DataTag.views.media',
    url(r'^medias/(?P<path>.*$)', 'media', name='media'),
)

urlpatterns += patterns('DataTag.views.tag',
    url(r'^tags/$', 'tag', {'tags': ''}, name='tag.root'),
    url(r'^tags/(?P<tags>.*)/$', 'tag', name='tag'),
)

urlpatterns += patterns('DataTag.views.main',
    url(r'^$', 'index', name='index'),
    url(r'^(?P<path>.*)/$', 'browse', name='browse'),
)
