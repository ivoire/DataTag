# -*- coding: utf-8 -*-
# vim: set ts=4

# Copyright 2015 Rémi Duraffort
# This file is part of DataTag.
#
# DataTag is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataTag is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with DataTag.  If not, see <http://www.gnu.org/licenses/>

from __future__ import unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _


class DTAuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(DTAuthenticationForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['username'].widget.attrs['placeholder'] = _('Username')
        self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['password'].widget.attrs['placeholder'] = _('Password')

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class DTPasswordChangeForm(PasswordChangeForm):
    """
    Override the default PasswordChangeForm in order to add HTML5 attributes.
    This is the only change done and needed
    """
    def __init__(self, *args, **kwargs):
        super(DTPasswordChangeForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['old_password'].widget.attrs['placeholder'] = _('Old password')
        self.fields['old_password'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['new_password1'].widget.attrs['placeholder'] = _('New password')
        self.fields['new_password2'].widget.attrs['placeholder'] = _('New password')

        self.fields['old_password'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control'


class DTUserCreationForm(UserCreationForm):
    """
    Override the default UserCreationForm in order to add HTML5 attributes.
    """
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(DTUserCreationForm, self).__init__(*args, **kwargs)
        # Add HTML5 attributes
        self.fields['username'].widget.attrs['placeholder'] = _('Username')
        self.fields['username'].widget.attrs['autofocus'] = 'autofocus'
        self.fields['password1'].widget.attrs['placeholder'] = _('Password')
        self.fields['password2'].widget.attrs['placeholder'] = _('Password')

        # email and first_name are required
        self.fields['email'].required = True
        self.fields['first_name'].required = True

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        """
        Create the new User
        The User is not activated until an admin activates it.
        """
        if not commit:
            raise NotImplementedError('Cannot create User with commit')
        user = super(DTUserCreationForm, self).save(commit=False)
        user.is_active = False
        user.save()
        return user


class DTUserUpdateForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super(DTUserUpdateForm, self).__init__(*args, **kwargs)
        # first_name and last_name are required
        self.fields['first_name'].required = True
        self.fields['first_name'].widget.attrs['autofocus'] = 'autofocus'

        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'


def register(request):
    if request.method == 'POST':
        user_form = DTUserCreationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            return render_to_response('DataTag/account/register_end.html', context_instance=RequestContext(request))
        else:
            messages.error(request, _("Some information are missing or mistyped"))
    else:
        user_form = DTUserCreationForm()

    return render_to_response('DataTag/account/register.html',
                              {'user_form': user_form},
                              context_instance=RequestContext(request))


@login_required
def password_change_done(request):
    messages.success(request, _('Password changed successfully'))
    return HttpResponseRedirect(reverse('accounts.profile'))


@login_required
def profile(request):
    return render_to_response('DataTag/account/profile.html',
                              context_instance=RequestContext(request))


@login_required
def update(request):
    if request.method == 'POST':
        user_form = DTUserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            # Print the message
            messages.success(request, _("Personnal information updated"))
            return HttpResponseRedirect(reverse('accounts.profile'))
    else:
        user_form = DTUserUpdateForm(instance=request.user)

    return render_to_response('DataTag/account/update.html',
                              {'user_form': user_form},
                              context_instance=RequestContext(request))
