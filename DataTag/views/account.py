# -*- coding: utf-8 -*-
# vim: set ts=4

from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
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


@login_required
def profile(request):
    return render_to_response('DataTag/account/profile.html',
                              context_instance=RequestContext(request))
