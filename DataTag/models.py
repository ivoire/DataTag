from __future__ import unicode_literals

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Media(models.Model):
    tags = models.ManyToManyField('Tag', blank=True, null=True)
    path = models.FilePathField(path=settings.MEDIA_ROOT, recursive=True,
                                max_length=256)

    def __str__(self):
        base_length = len(settings.MEDIA_ROOT)
        tags_str = ', '.join([tag.name for tag in self.tags.all()])
        return "%s: %s" % (self.path[base_length+1:], tags_str)

    def get_absolute_url(self):
        base_length = len(settings.MEDIA_ROOT)
        return reverse('media', args=[self.path[base_length+1:]])

    def is_visible_to(self, user):
        """
        Return true if this medias is visible for the given user
        """
        # Is the user anonymous?
        if user.is_anonymous():
            if self.tags.filter(is_public=True).exists():
                return True
        else:
            user_groups_set = set(user.groups.all())
            for tag in self.tags.all():
                if tag.is_public:
                    return True
                tag_groups_set = set(tag.groups.all())
                # A tag without groups is visible to all authenticated users
                if not tag_groups_set:
                    return True
                if tag_groups_set & user_groups_set:
                    return True
            # A media without tags is visible to all authenticated users
            if not self.tags.all().exists():
                return True
        return False


@python_2_unicode_compatible
class Tag(models.Model):
    # TODO: name should be unique !
    name = models.CharField(max_length=128)
    groups = models.ManyToManyField(Group, blank=True, null=True)
    is_public = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % (self.name)

    def get_absolute_url(self):
        return reverse('tags.details', args=[self.name])

    def is_visible_to(self, user):
        """
        Return True if this tag is visible to the given user
        """
        if self.is_public:
            return True
        if user.is_anonymous():
            return False

        tag_groups_set = set(self.groups.all())
        if not tag_groups_set:
            return True
        user_groups_set = set(user.groups.all())
        if tag_groups_set & user_groups_set:
            return True
        return False
