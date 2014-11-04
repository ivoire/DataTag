from __future__ import unicode_literals

from django.contrib import admin

from DataTag.models import Media, Tag


admin.site.register(Media)
admin.site.register(Tag)
