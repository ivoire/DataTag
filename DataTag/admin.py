from __future__ import unicode_literals

from django.contrib import admin

from DataTag.models import Media, Tag


class MediaAdmin(admin.ModelAdmin):
    list_display = ('path', 'tag_list')
    list_filter = ('tags',)
    filter_horizontal = ('tags',)
    search_fields = ('path',)

    def tag_list(self, obj):
        return "|".join([tag.name for tag in obj.tags.all()])


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'group_list', 'is_public')
    list_filter = ('groups',)
    filter_horizontal = ('groups',)
    def group_list(self, obj):
        return "|".join([tag.name for tag in obj.groups.all()])

admin.site.register(Media, MediaAdmin)
admin.site.register(Tag, TagAdmin)
