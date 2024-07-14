from functools import wraps

from django.shortcuts import render
from django.utils.log import log_response


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
