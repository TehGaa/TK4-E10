import functools
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseBadRequest

def login_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if (request.COOKIES.get('role') != None and
            request.COOKIES.get('username') != None):
            return func(*args, **kwargs)
        else:
            return HttpResponseBadRequest("Not logged in")
    return wrapper

def login_required_as_role(role):
    def wrapper(func):
        def next_wrapper(*args, **kwargs):
            request = args[0]
            if (request.COOKIES.get('role') == role and
                request.COOKIES.get('username') != None):
                return func(*args, **kwargs)
            else:
                return HttpResponseBadRequest("Unauthorized role")
    return wrapper