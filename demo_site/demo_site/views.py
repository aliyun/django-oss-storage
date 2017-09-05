# -*- coding: utf-8 -*-

from django.contrib import messages
from django.shortcuts import redirect

def home(request):
    messages.add_message(request, messages.WARNING,
        'Default user & password are both "admin".')
    return redirect('admin:index')
