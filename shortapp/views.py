import hashlib
import redis
import datetime
import uuid
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache  
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import BaseThrottle
from .models import ShortenedURL
from django.views.decorators.csrf import csrf_exempt


# Redis client for rate limiting
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0, decode_responses=True)

# Generate short code
def generate_short_code(url):
    unique_str = url + str(uuid.uuid4())  # Combine UUID to generate a unique string to avoid hash collision.
    return hashlib.md5(unique_str.encode()).hexdigest()[:6]

# Custom rate limiting using Redis
class RedisRateThrottle(BaseThrottle):
    rate_limit = settings.RATE_LIMIT  # Allow max 10 requests per minute
    window_size = settings.WINDOW_SIZE  # Time window in seconds

    def allow_request(self, request, view):
        ip = request.META.get('REMOTE_ADDR')
        key = f"rate_limit:{ip}"
        request_count = redis_client.get(key)
        
        if request_count is None:
            redis_client.setex(key, self.window_size, 1)
            return True
        elif int(request_count) < self.rate_limit:
            redis_client.incr(key)
            return True
        else:
            return False

# API to create short URLs
class CreateShortURLView(APIView):
    throttle_classes = [RedisRateThrottle]  # Using Redis-based rate limiting
    
    def post(self, request):
        original_url = request.data.get("original_url")
        
        # Validate URL
        validator = URLValidator()
        try:
            validator(original_url)
        except ValidationError:
            return Response({"success": False, "reason": "Invalid URL"}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(original_url) > 2048:
            return Response({"success": False, "reason": "URL too long"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate unique short code
        short_code = generate_short_code(original_url)
        
        while ShortenedURL.objects.filter(short_code=short_code).exists():
            short_code = generate_short_code(original_url)
        
        expiration_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=settings.DAY)
        short_url = ShortenedURL.objects.create(original_url=original_url, short_code=short_code, expiration_date=expiration_date)
        full_short_url = request.build_absolute_uri(f'/{short_code}')
        # Cache the shortened URL in Redis
        cache.set(f"short_url:{short_code}", original_url, timeout=86400)
        return Response({
            "short_url": full_short_url,
            "expiration_date": short_url.expiration_date,
            "success": True
        }, status=status.HTTP_201_CREATED)

# API to handle redirection
class RedirectShortURLView(APIView):

    def get(self, request, short_code):
        cache_key = f"short_url:{short_code}"
        cached_url = cache.get(cache_key)
        
        if cached_url:
            # If the cached URL exists, we still need to check if it's expired.
            short_url = ShortenedURL.objects.filter(short_code=short_code).first()
            if short_url and short_url.is_expired():
                # If the short URL is expired, remove it from cache and return 410 Gone
                cache.delete(cache_key)
                return Response({"success": False, "reason": "Short URL expired"}, status=status.HTTP_410_GONE)
        
        short_url = ShortenedURL.objects.filter(short_code=short_code).first()
        if not short_url:
            return Response({"success": False, "reason": "Short URL not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if short_url.is_expired():
            return Response({"success": False, "reason": "Short URL expired"}, status=status.HTTP_410_GONE)
        
        cache.set(cache_key, short_url.original_url, timeout=86400)
        return redirect(short_url.original_url)
