import redis
from django.conf import settings
from django.db import OperationalError, connections
from django.http import JsonResponse


def health_check(request):
    """
    Checks the health of the application and its dependencies.
    """
    db_ok = True
    try:
        for conn in connections.all():
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
    except OperationalError:
        db_ok = False

    cache_ok = True
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            socket_connect_timeout=1,
        )
        r.ping()
    except (redis.exceptions.ConnectionError, redis.exceptions.BusyLoadingError):
        cache_ok = False

    services = {'database': db_ok, 'cache': cache_ok}
    http_status = 200 if db_ok and cache_ok else 503
    return JsonResponse(services, status=http_status)
