from functools import wraps

from django.shortcuts import render
from django.utils.log import log_response


def bad_request_view(request, exception=None):
    return render(request, 'http_status_codes/400.html', status=400)


def permission_denied_view(request, exception=None):
    return render(request, 'http_status_codes/403.html', status=403)


def page_not_found_view(request, exception=None):
    return render(request, 'http_status_codes/404.html', status=404)


def custom_require_http_methods(request_method_list):
    """
    This function is almost entirely copied from django.views.decorators.http.require_http_methods.
    The difference is the return of the render function instead of HttpResponseNotAllowed.
    """

    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if request.method not in request_method_list:
                response = render(request, 'http_status_codes/405.html', status=405)
                log_response(
                    "Method Not Allowed (%s): %s",
                    request.method,
                    request.path,
                    response=response,
                    request=request,
                )
                return response
            return func(request, *args, **kwargs)

        return inner

    return decorator
