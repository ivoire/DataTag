# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.conf.urls import include, patterns, url
from django.core.urlresolvers import reverse_lazy


urlpatterns = patterns('DataTag.views.main',
    url(r'^$', 'index', name='index'),
)

urlpatterns += patterns('DataTag.views.media',
    url(r'^medias/(?P<path>.*$)', 'media', name='media'),
)

urlpatterns += patterns('DataTag.views.tag',
    url(r'^tags/$', 'tag', {'path': ''}, name='tags.root'),
    url(r'^tags/(?P<path>.*)/$', 'tag', name='tags.details'),
    url(r'^(?P<path>.*)/$', 'browse', name='tags.browse'),
)
