from django.core.cache import cache

CARS_CACHE_TIMEOUT = 60 * 15
_VERSION_KEY = "cars:version"


def get_cars_cache_version():
    return cache.get_or_set(_VERSION_KEY, 1, timeout=None)


def invalidate_cars_cache() -> None:
    try:
        cache.incr(_VERSION_KEY)
    except ValueError:
        cache.set(_VERSION_KEY, 1, timeout=None)
