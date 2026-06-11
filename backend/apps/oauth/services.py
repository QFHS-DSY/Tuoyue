from __future__ import annotations

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests
from django.core.cache import cache


class PlatformRateLimitError(Exception):
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = max(int(retry_after or 1), 1)


class PlatformAPIClient:
    RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

    def __init__(
        self,
        platform: str,
        base_url: str,
        *,
        rate_limit_capacity: int = 10,
        rate_limit_window_seconds: int = 1,
        timeout: int = 10,
        max_retries: int = 3,
    ):
        self.platform = platform
        self.base_url = (base_url or "").rstrip("/")
        self.rate_limit_capacity = max(int(rate_limit_capacity or 1), 1)
        self.rate_limit_window_seconds = max(int(rate_limit_window_seconds or 1), 1)
        self.timeout = max(int(timeout or 1), 1)
        self.max_retries = max(int(max_retries or 0), 0)

    def _bucket_key(self, scope: str) -> str:
        safe_scope = (scope or "default").replace(" ", "_")
        return f"oauth:bucket:{self.platform}:{safe_scope}"

    def _acquire_token_delay(self, scope: str) -> float:
        now = time.time()
        refill_rate = float(self.rate_limit_capacity) / float(self.rate_limit_window_seconds)
        state = cache.get(self._bucket_key(scope)) or {}
        tokens = float(state.get("tokens", self.rate_limit_capacity))
        updated_at = float(state.get("updated_at", now))
        elapsed = max(now - updated_at, 0.0)
        tokens = min(float(self.rate_limit_capacity), tokens + elapsed * refill_rate)
        if tokens < 1.0:
            cache.set(
                self._bucket_key(scope),
                {"tokens": tokens, "updated_at": now},
                timeout=self.rate_limit_window_seconds * 2,
            )
            return max((1.0 - tokens) / refill_rate, 0.0)
        cache.set(
            self._bucket_key(scope),
            {"tokens": tokens - 1.0, "updated_at": now},
            timeout=self.rate_limit_window_seconds * 2,
        )
        return 0.0

    @staticmethod
    def _retry_after_seconds(header_value: str | None) -> int:
        try:
            return max(int(header_value or 0), 0)
        except Exception:
            return 0

    def _backoff_seconds(self, attempt: int, retry_after: int = 0) -> float:
        if retry_after > 0:
            return float(retry_after)
        return min(2 ** attempt, 8)

    def _build_url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        if not self.base_url:
            raise ValueError(f"{self.platform} API base url is not configured")
        if not path:
            return self.base_url
        return f"{self.base_url}/{path.lstrip('/')}"

    @staticmethod
    def _response_payload(response: requests.Response) -> Any:
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            return {"raw_text": response.text}

    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json_payload: dict[str, Any] | None = None,
        scope: str = "default",
        timeout: int | None = None,
    ) -> Any:
        last_exception: Exception | None = None
        for attempt in range(self.max_retries + 1):
            delay = self._acquire_token_delay(scope)
            if delay > 0:
                time.sleep(delay)
            try:
                response = requests.request(
                    method=method.upper(),
                    url=self._build_url(path),
                    headers=headers,
                    params=params,
                    data=data,
                    json=json_payload,
                    timeout=timeout or self.timeout,
                )
            except requests.RequestException as exc:
                last_exception = exc
                if attempt >= self.max_retries:
                    raise
                time.sleep(self._backoff_seconds(attempt))
                continue

            if response.status_code in self.RETRYABLE_STATUS_CODES:
                retry_after = self._retry_after_seconds(response.headers.get("Retry-After"))
                if attempt >= self.max_retries:
                    if response.status_code == 429:
                        raise PlatformRateLimitError(
                            f"{self.platform} upstream rate limited",
                            retry_after=retry_after or 60,
                        )
                    response.raise_for_status()
                time.sleep(self._backoff_seconds(attempt, retry_after=retry_after))
                continue

            response.raise_for_status()
            return self._response_payload(response)

        if last_exception is not None:
            raise last_exception
        raise RuntimeError(f"{self.platform} request exhausted retries")

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)


def build_mock_1688_detail(item_id: str, source_url: str = "") -> dict[str, Any]:
    suffix = "".join(ch for ch in str(item_id) if ch.isdigit())[-6:] or "168800"
    seed = int(suffix)
    price_a = Decimal("19.90") + Decimal(seed % 200) / Decimal("10")
    price_b = price_a - Decimal("1.50")
    main_image = f"https://mock-cdn.local/1688/{item_id}/main.jpg"
    skus = [
        {
            "sku": f"{item_id}-BLK-M",
            "title": "Black / M",
            "price": str(price_a.quantize(Decimal('0.01'))),
            "stock": 80 + seed % 20,
            "attributes": {"color": "black", "size": "M"},
            "image": f"https://mock-cdn.local/1688/{item_id}/black-m.jpg",
        },
        {
            "sku": f"{item_id}-WHT-L",
            "title": "White / L",
            "price": str(price_b.quantize(Decimal('0.01'))),
            "stock": 60 + seed % 15,
            "attributes": {"color": "white", "size": "L"},
            "image": f"https://mock-cdn.local/1688/{item_id}/white-l.jpg",
        },
    ]
    return {
        "item_id": str(item_id),
        "title": f"1688 Demo Item {item_id}",
        "main_image": main_image,
        "images": [main_image] + [sku["image"] for sku in skus],
        "price": skus[0]["price"],
        "stock": sum(int(sku["stock"]) for sku in skus),
        "price_ladder": [
            {"min_quantity": 2, "price": skus[0]["price"]},
            {"min_quantity": 10, "price": skus[1]["price"]},
        ],
        "attributes": {
            "brand": "Demo Factory",
            "material": "polyester",
            "source_url": source_url,
        },
        "skus": skus,
        "mocked": True,
    }


def map_product_to_shein_payload(product: Any) -> dict[str, Any]:
    images = list(getattr(product, "images", None) or [])
    attributes = dict(getattr(product, "attributes", None) or {})
    variant_items = []
    variants = getattr(product, "variants", None)
    if variants is not None:
        iterable = variants.all() if hasattr(variants, "all") else variants
        for variant in iterable:
            variant_items.append(
                {
                    "seller_sku": getattr(variant, "sku", ""),
                    "title": getattr(variant, "title", ""),
                    "price": str(getattr(variant, "price", "0")),
                    "stock": int(getattr(variant, "stock", 0) or 0),
                    "attributes": getattr(variant, "attributes", {}) or {},
                }
            )
    if not variant_items:
        variant_items.append(
            {
                "seller_sku": getattr(product, "platform_product_id", ""),
                "title": getattr(product, "title", ""),
                "price": str(getattr(product, "price", "0")),
                "stock": int(getattr(product, "stock", 0) or 0),
                "attributes": attributes,
            }
        )
    return {
        "product_name": getattr(product, "title", ""),
        "seller_spu": getattr(product, "platform_product_id", ""),
        "description": attributes.get("description") or getattr(product, "title", ""),
        "images": images,
        "attributes": attributes,
        "skus": variant_items,
    }


@dataclass
class MockListingResult:
    listing_id: str
    status: str
    shop_id: str
    mocked: bool
    degraded: bool
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "listing_id": self.listing_id,
            "status": self.status,
            "shop_id": self.shop_id,
            "mocked": self.mocked,
            "degraded": self.degraded,
            "payload": self.payload,
        }
