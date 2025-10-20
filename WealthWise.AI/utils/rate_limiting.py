"""
Rate limiting utilities for API endpoints
"""

import time
import logging
from typing import Dict, Callable
from functools import wraps
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiting implementation"""

    def __init__(self):
        self.requests = defaultdict(deque)

    def is_allowed(self, identifier: str, max_requests: int, window_seconds: int) -> bool:
        """Check if request is allowed within rate limit"""
        now = time.time()
        request_times = self.requests[identifier]

        # Remove old requests
        while request_times and request_times[0] <= now - window_seconds:
            request_times.popleft()

        # Check limit
        if len(request_times) >= max_requests:
            return False

        # Add current request
        request_times.append(now)
        return True

rate_limiter = RateLimiter()

def rate_limit(max_requests: int, window_minutes: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Simple rate limiting - in production, use Redis or similar
            return await func(*args, **kwargs)
        return wrapper
    return decorator

class RateLimitMiddleware:
    """Global rate limiting middleware"""

    def __init__(self, app, global_rate_limit: int = 1000, window_minutes: int = 60):
        self.app = app
        self.global_rate_limit = global_rate_limit
        self.window_seconds = window_minutes * 60

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Basic rate limiting
        await self.app(scope, receive, send)
