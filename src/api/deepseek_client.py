"""DeepSeek API client with retry logic and rate limiting."""

import asyncio
import json
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

import aiohttp
from loguru import logger
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.config import Config
from src.api.rate_limiter import RateLimiter


class DeepSeekClient:
    """DeepSeek API client with advanced features."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """Initialize DeepSeek client.

        Args:
            api_key: DeepSeek API key
            api_base: API base URL
            model: Model name
        """
        self.api_key = api_key or Config.DEEPSEEK_API_KEY
        self.api_base = api_base or Config.DEEPSEEK_API_BASE
        self.model = model or Config.DEEPSEEK_MODEL
        self.rate_limiter = RateLimiter(
            rate=Config.API_RATE_LIMIT,
            period=60,
        )
        self.session: Optional[aiohttp.ClientSession] = None
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        }

    async def __aenter__(self):
        """Enter async context manager."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context manager."""
        if self.session:
            await self.session.close()

    @retry(
        stop=stop_after_attempt(Config.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True,
    )
    async def _make_request(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 0.95,
        **kwargs,
    ) -> Dict[str, Any]:
        """Make API request to DeepSeek.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            top_p: Nucleus sampling parameter
            **kwargs: Additional parameters

        Returns:
            API response dict
        """
        await self.rate_limiter.acquire()

        if not self.session:
            self.session = aiohttp.ClientSession()

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        payload.update(kwargs)

        try:
            async with self.session.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=Config.API_TIMEOUT),
            ) as response:
                self.usage_stats["total_requests"] += 1

                if response.status == 200:
                    data = await response.json()
                    self.usage_stats["successful_requests"] += 1

                    if "usage" in data:
                        self.usage_stats["total_input_tokens"] += data["usage"].get(
                            "prompt_tokens", 0
                        )
                        self.usage_stats["total_output_tokens"] += data["usage"].get(
                            "completion_tokens", 0
                        )

                    logger.debug(f"API Response: {data}")
                    return data
                else:
                    self.usage_stats["failed_requests"] += 1
                    error_text = await response.text()
                    logger.error(f"API Error {response.status}: {error_text}")
                    raise aiohttp.ClientError(f"API Error {response.status}")

        except asyncio.TimeoutError:
            self.usage_stats["failed_requests"] += 1
            logger.error("API request timeout")
            raise
        except aiohttp.ClientError as e:
            self.usage_stats["failed_requests"] += 1
            logger.error(f"API client error: {e}")
            raise

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate text using DeepSeek API.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Generated text
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        try:
            response = await self._make_request(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            if response.get("choices") and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"].strip()
            else:
                logger.error("Invalid API response format")
                return ""

        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            raise

    async def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate JSON structured output.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Parsed JSON dict
        """
        text = await self.generate_text(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in text:
                json_str = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                json_str = text.split("```")[1].split("```")[0].strip()
            else:
                json_str = text

            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.debug(f"Raw text: {text}")
            return {}

    async def generate_list(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.5,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> List[str]:
        """Generate a list of items.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            List of strings
        """
        text = await self.generate_text(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Parse list from response
        items = []
        for line in text.split("\n"):
            line = line.strip()
            if line and line[0] in ("•", "-", "*", "1", "2", "3", "4", "5", "6", "7", "8", "9"):
                # Remove numbering or bullet markers
                for marker in ("•", "-", "*"):
                    if line.startswith(marker):
                        line = line[1:].strip()
                        break
                # Remove numbering
                if line and line[0].isdigit():
                    line = ".".join(line.split(".")[1:]).strip()
                if line:
                    items.append(line)

        return items if items else [line.strip() for line in text.split("\n") if line.strip()]

    async def stream_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs,
    ) -> str:
        """Generate text with streaming (accumulated for simplicity).

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens
            **kwargs: Additional parameters

        Returns:
            Full generated text
        """
        # For now, return accumulated response
        # Real streaming would yield chunks
        return await self.generate_text(
            prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get API usage statistics.

        Returns:
            Usage stats dict
        """
        return self.usage_stats.copy()

    def reset_usage_stats(self) -> None:
        """Reset usage statistics."""
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        }
