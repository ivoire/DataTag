from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models


class Media(models.Model):
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    path = models.FilePathField(path=settings.MEDIA_ROOT, recursive=True,
                                max_length=256)

    def __str__(self):
        base_length = len(settings.MEDIA_ROOT)
        tags_str = ', '.join([tag.name for tag in self.tags.all()])
        return "%s: %s" % (self.path[base_length+1:], tags_str)

    def get_absolute_url(self):
        return reverse('media', args=[self.path[len(settings.MEDIA_ROOT) + 1:]])


class Tag(models.Model):
    # TODO: name should be unique !
    name = models.CharField(max_length=128)
    groups = models.ManyToManyField(Group, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('tag', args=[self.name])

    def get_browse_url(self):
        return reverse('browse', args=[self.name])
