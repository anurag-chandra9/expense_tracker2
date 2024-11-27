from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json

def cache_key_with_params(prefix, *args, **kwargs):
    """Generate a cache key based on the prefix and parameters."""
    key_parts = [prefix]
    if args:
        key_parts.extend([str(arg) for arg in args])
    if kwargs:
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()

def cached_view(timeout=None):
    """
    Cache decorator for views that takes request parameters into account.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Create a cache key based on the view name and request parameters
            cache_prefix = f"view:{view_func.__name__}"
            
            # Include GET parameters in cache key
            params = dict(request.GET.items())
            
            # Include URL parameters
            params.update(kwargs)
            
            # Generate cache key
            cache_key = cache_key_with_params(cache_prefix, **params)
            
            # Try to get the response from cache
            response = cache.get(cache_key)
            
            if response is None:
                # If not in cache, generate response and cache it
                response = view_func(request, *args, **kwargs)
                cache.set(cache_key, response, timeout or settings.CACHE_TTL)
            
            return response
        return _wrapped_view
    return decorator

def invalidate_cache_prefix(prefix):
    """
    Invalidate all cache keys starting with the given prefix.
    """
    keys = cache.keys(f"{prefix}:*")
    if keys:
        cache.delete_many(keys)

def cache_result(prefix, timeout=None):
    """
    Cache decorator for functions that returns JSON-serializable results.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = cache_key_with_params(prefix, *args, **kwargs)
            result = cache.get(cache_key)
            
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, json.dumps(result), timeout or settings.CACHE_TTL)
            else:
                result = json.loads(result)
                
            return result
        return wrapper
    return decorator
