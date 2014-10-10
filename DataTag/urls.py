# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.conf.urls import include, patterns, url
from django.core.urlresolvers import reverse_lazy


urlpatterns = patterns('DataTag.views.main',
    url(r'^$', 'index', name='index'),
)
