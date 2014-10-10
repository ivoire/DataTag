from __future__ import unicode_literals

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db import models


class Tag(models.Model):
    name = models.CharField(max_length=128)
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children')
    groups = models.ManyToManyField(Group, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def clean(self):
        if self.parent.pk == self.pk:
            raise ValidationError({'parent': ['Parent cannot be self']})

    def __str__(self):
        if self.parent:
            return "%s (%s)" % (self.name, self.parent.name)
        else:
            return "%s" % (self.name)
