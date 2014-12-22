from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin

from DataTag.models import Media, Tag


class MediaAdmin(admin.ModelAdmin):
    list_display = ('path_short', 'tag_list', 'date')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    search_fields = ('path',)

    def path_short(self, obj):
        return obj.path[len(settings.MEDIA_ROOT)+1:]

    def tag_list(self, obj):
        return "|".join([tag.name for tag in obj.tags.all()])


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_list', 'is_public', 'is_root')
    list_filter = ('groups',)
    filter_horizontal = ('groups',)

    def group_list(self, obj):
        return "|".join([tag.name for tag in obj.groups.all()])

admin.site.register(Media, MediaAdmin)
admin.site.register(Tag, TagAdmin)
