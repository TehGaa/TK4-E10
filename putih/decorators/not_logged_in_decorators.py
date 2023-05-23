from django.http import HttpResponseBadRequest

def not_login_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if (request.COOKIES.get('role') == None):
            return func(*args, **kwargs)
        else:
            return HttpResponseBadRequest("Already Logged In")
    return wrapper