"""Rate limiter for API requests."""

import asyncio
import time
from collections import deque
from typing import Deque
from loguru import logger


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, rate: int = 10, period: int = 60):
        """Initialize rate limiter.

        Args:
            rate: Number of requests allowed
            period: Time period in seconds
        """
        self.rate = rate
        self.period = period
        self.requests: Deque[float] = deque()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a request.

        Blocks if rate limit exceeded.
        """
        async with self.lock:
            now = time.time()
            cutoff = now - self.period

            # Remove old requests
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()

            # Check if we've hit the limit
            if len(self.requests) >= self.rate:
                sleep_time = self.requests[0] + self.period - now
                if sleep_time > 0:
                    logger.debug(f"Rate limit: sleeping for {sleep_time:.2f}s")
                    await asyncio.sleep(sleep_time)
                    # Recursive call to re-check after sleep
                    await self.acquire()
                    return

            self.requests.append(now)

    def get_stats(self) -> dict:
        """Get current rate limiter stats.

        Returns:
            Stats dict
        """
        return {
            "requests_in_period": len(self.requests),
            "rate_limit": self.rate,
            "period_seconds": self.period,
        }
