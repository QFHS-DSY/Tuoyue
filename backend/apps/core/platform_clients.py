from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode

from django.conf import settings

from apps.oauth.services import (
    MockListingResult,
    PlatformAPIClient,
    PlatformRateLimitError,
    build_mock_1688_detail,
)


@dataclass
class BasePlatformClient:
    platform: str

    def get_oauth_authorize_url(self, state: str) -> str:
        return f"https://auth.{self.platform}.mock/oauth/authorize?client_id=demo&state={state}&response_type=code"

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        timestamp = int(time.time())
        return {
            "access_token": f"{self.platform}_access_{code}_{timestamp}",
            "refresh_token": f"{self.platform}_refresh_{code}_{timestamp}",
            "expires_in": 7200,
            "account_id": "default",
        }

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        timestamp = int(time.time())
        return {
            "access_token": f"{self.platform}_refreshed_access_{timestamp}",
            "refresh_token": f"{self.platform}_refreshed_refresh_{timestamp}",
            "expires_in": 7200,
        }

    def fetch_products(self, target_ids: list[str]) -> list[dict[str, Any]]:
        data = []
        for item_id in target_ids:
            data.append(
                {
                    "platform_product_id": str(item_id),
                    "title": f"{self.platform.upper()} Product {item_id}",
                    "images": [f"https://img.mock/{self.platform}/{item_id}.jpg"],
                    "attributes": {"color": "black", "size": "M"},
                    "price": "99.90",
                    "stock": 200,
                }
            )
        return data

    def fetch_inventory(self, warehouse_id: str) -> list[dict[str, Any]]:
        return [
            {"platform_product_id": "demo-1001", "stock": 88},
            {"platform_product_id": "demo-1002", "stock": 66},
        ]

    def fetch_order_list(self, access_token: str, page_size: int = 50, cursor: str = "") -> dict[str, Any]:
        return {"orders": [], "next_cursor": "", "has_more": False}


@dataclass
class TikTokPlatformClient(BasePlatformClient):
    def _client_key(self) -> str:
        return (getattr(settings, "TIKTOK_CLIENT_KEY", "") or "").strip()

    def _client_secret(self) -> str:
        return (getattr(settings, "TIKTOK_CLIENT_SECRET", "") or "").strip()

    def _redirect_uri(self) -> str:
        return (getattr(settings, "TIKTOK_REDIRECT_URI", "") or "").strip()

    def _auth_base_url(self) -> str:
        return (getattr(settings, "TIKTOK_AUTH_BASE_URL", "https://www.tiktok.com/v2/auth/authorize/") or "").strip()

    def _api_base_url(self) -> str:
        return (getattr(settings, "TIKTOK_API_BASE_URL", "https://open.tiktokapis.com/v2/") or "").strip()

    def _scopes(self) -> str:
        return (getattr(settings, "TIKTOK_SCOPES", "user.info.basic,video.list") or "user.info.basic,video.list").strip()

    def _http_client(self) -> PlatformAPIClient:
        return PlatformAPIClient(
            platform=self.platform,
            base_url=self._api_base_url(),
            timeout=int(getattr(settings, "PLATFORM_API_TIMEOUT_SECONDS", 10)),
            max_retries=int(getattr(settings, "PLATFORM_API_MAX_RETRIES", 3)),
        )

    def _validate_config(self) -> None:
        if not self._client_key() or not self._client_secret() or not self._redirect_uri():
            raise ValueError(
                "TikTok OAuth config is incomplete. Please set TIKTOK_CLIENT_KEY/TIKTOK_CLIENT_SECRET/TIKTOK_REDIRECT_URI"
            )

    def get_oauth_authorize_url(self, state: str) -> str:
        self._validate_config()
        query = urlencode(
            {
                "client_key": self._client_key(),
                "redirect_uri": self._redirect_uri(),
                "response_type": "code",
                "scope": self._scopes(),
                "state": state,
            }
        )
        return f"{self._auth_base_url()}?{query}"

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        self._validate_config()
        payload = self._http_client().post(
            "oauth/token/",
            data={
                "client_key": self._client_key(),
                "client_secret": self._client_secret(),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self._redirect_uri(),
            },
        )
        data = payload.get("data", payload)
        open_id = data.get("open_id") or data.get("openid") or "default"
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": int(data.get("expires_in", 7200)),
            "account_id": open_id,
        }

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        self._validate_config()
        payload = self._http_client().post(
            "oauth/token/",
            data={
                "client_key": self._client_key(),
                "client_secret": self._client_secret(),
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )
        data = payload.get("data", payload)
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_in": int(data.get("expires_in", 7200)),
        }

    def fetch_order_list(self, access_token: str, page_size: int = 50, cursor: str = "") -> dict[str, Any]:
        self._validate_config()
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"page_size": max(1, min(int(page_size or 50), 100))}
        if cursor:
            params["cursor"] = cursor
        payload = self._http_client().get("order/list/", headers=headers, params=params, scope="order-list")
        if str(payload.get("code", "")) in {"rate_limited", "too_many_requests"}:
            retry_after = int(payload.get("data", {}).get("retry_after", 60))
            raise PlatformRateLimitError("TikTok orderlist rate limited", retry_after=retry_after)
        data = payload.get("data", payload)
        return {
            "orders": data.get("orders", []),
            "next_cursor": data.get("next_cursor") or "",
            "has_more": bool(data.get("has_more")),
        }


@dataclass
class SheinPlatformClient(BasePlatformClient):
    def _client_id(self) -> str:
        return (getattr(settings, "SHEIN_CLIENT_ID", "") or "").strip()

    def _client_secret(self) -> str:
        return (getattr(settings, "SHEIN_CLIENT_SECRET", "") or "").strip()

    def _redirect_uri(self) -> str:
        return (getattr(settings, "SHEIN_REDIRECT_URI", "") or "").strip()

    def _auth_base_url(self) -> str:
        return (getattr(settings, "SHEIN_AUTH_BASE_URL", "") or "").strip()

    def _api_base_url(self) -> str:
        return (getattr(settings, "SHEIN_API_BASE_URL", "") or "").strip()

    def _http_client(self) -> PlatformAPIClient:
        return PlatformAPIClient(
            platform=self.platform,
            base_url=self._api_base_url(),
            rate_limit_capacity=int(getattr(settings, "SHEIN_RATE_LIMIT_CAPACITY", 10)),
            rate_limit_window_seconds=int(getattr(settings, "SHEIN_RATE_LIMIT_WINDOW_SECONDS", 1)),
            timeout=int(getattr(settings, "PLATFORM_API_TIMEOUT_SECONDS", 10)),
            max_retries=int(getattr(settings, "PLATFORM_API_MAX_RETRIES", 3)),
        )

    def _validate_config(self) -> None:
        missing = []
        if not self._client_id():
            missing.append("SHEIN_CLIENT_ID")
        if not self._client_secret():
            missing.append("SHEIN_CLIENT_SECRET")
        if not self._redirect_uri():
            missing.append("SHEIN_REDIRECT_URI")
        if missing and not getattr(settings, "DEMO_MODE", False):
            raise ValueError(f"Shein OAuth config is incomplete: {', '.join(missing)}")

    def get_oauth_authorize_url(self, state: str) -> str:
        self._validate_config()
        if not self._auth_base_url():
            return f"https://auth.shein.mock/oauth/authorize?client_id={self._client_id() or 'demo'}&state={state}"
        query = urlencode(
            {
                "client_id": self._client_id(),
                "redirect_uri": self._redirect_uri(),
                "response_type": "code",
                "state": state,
            }
        )
        return f"{self._auth_base_url()}?{query}"

    def exchange_code_for_token(self, code: str) -> dict[str, Any]:
        self._validate_config()
        if not self._api_base_url():
            timestamp = int(time.time())
            return {
                "access_token": f"shein_access_{code}_{timestamp}",
                "refresh_token": f"shein_refresh_{code}_{timestamp}",
                "expires_in": 7200,
                "account_id": "default",
            }
        payload = self._http_client().post(
            getattr(settings, "SHEIN_TOKEN_PATH", "oauth/token"),
            data={
                "client_id": self._client_id(),
                "client_secret": self._client_secret(),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self._redirect_uri(),
            },
        )
        data = payload.get("data", payload)
        return {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "expires_in": int(data.get("expires_in", 7200)),
            "account_id": data.get("shop_id") or data.get("merchant_id") or "default",
        }

    def refresh_token(self, refresh_token: str) -> dict[str, Any]:
        self._validate_config()
        if not self._api_base_url():
            timestamp = int(time.time())
            return {
                "access_token": f"shein_refreshed_access_{timestamp}",
                "refresh_token": f"shein_refreshed_refresh_{timestamp}",
                "expires_in": 7200,
            }
        payload = self._http_client().post(
            getattr(settings, "SHEIN_REFRESH_PATH", "oauth/token/refresh"),
            data={
                "client_id": self._client_id(),
                "client_secret": self._client_secret(),
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        data = payload.get("data", payload)
        return {
            "access_token": data["access_token"],
            "refresh_token": data.get("refresh_token", refresh_token),
            "expires_in": int(data.get("expires_in", 7200)),
        }

    def publish_listing(self, payload: dict[str, Any], *, shop_id: str = "", access_token: str = "") -> dict[str, Any]:
        result = MockListingResult(
            listing_id=f"shein-demo-{int(time.time())}",
            status="draft",
            shop_id=shop_id or "default",
            mocked=True,
            degraded=False,
            payload=payload,
        )
        if getattr(settings, "DEMO_MODE", False):
            return result.as_dict()

        self._validate_config()
        if not access_token:
            raise ValueError("Shein access token is required before publishing a listing")

        try:
            response_payload = self._http_client().post(
                getattr(settings, "SHEIN_LISTING_PATH", "products/listings"),
                headers={"Authorization": f"Bearer {access_token}"},
                json_payload={"shop_id": shop_id or "default", **payload},
                scope=shop_id or "default",
            )
        except Exception:
            if getattr(settings, "DEMO_MODE", False):
                result.degraded = True
                return result.as_dict()
            raise

        data = response_payload.get("data", response_payload)
        return {
            "listing_id": data.get("listing_id") or data.get("id") or f"shein-{int(time.time())}",
            "status": data.get("status") or "submitted",
            "shop_id": shop_id or "default",
            "mocked": False,
            "degraded": False,
            "payload": payload,
        }


@dataclass
class Alibaba1688PlatformClient(BasePlatformClient):
    def _api_base_url(self) -> str:
        return (getattr(settings, "ALIBABA1688_API_BASE_URL", "") or "").strip()

    def _app_key(self) -> str:
        return (getattr(settings, "ALIBABA1688_APP_KEY", "") or "").strip()

    def _app_secret(self) -> str:
        return (getattr(settings, "ALIBABA1688_APP_SECRET", "") or "").strip()

    def _http_client(self) -> PlatformAPIClient:
        return PlatformAPIClient(
            platform=self.platform,
            base_url=self._api_base_url(),
            rate_limit_capacity=int(getattr(settings, "ALIBABA1688_RATE_LIMIT_CAPACITY", 10)),
            rate_limit_window_seconds=int(getattr(settings, "ALIBABA1688_RATE_LIMIT_WINDOW_SECONDS", 1)),
            timeout=int(getattr(settings, "PLATFORM_API_TIMEOUT_SECONDS", 10)),
            max_retries=int(getattr(settings, "PLATFORM_API_MAX_RETRIES", 3)),
        )

    def _normalize_detail(self, payload: dict[str, Any], *, item_id: str, source_url: str) -> dict[str, Any]:
        data = payload.get("data", payload)
        images = [img for img in (data.get("images") or [data.get("main_image")]) if img]
        attributes = data.get("attributes") or {}
        raw_skus = data.get("skus") or data.get("sku_infos") or []
        normalized_skus = []
        for index, raw_sku in enumerate(raw_skus, start=1):
            sku_code = str(raw_sku.get("sku") or raw_sku.get("sku_id") or f"{item_id}-{index}")
            normalized_skus.append(
                {
                    "sku": sku_code,
                    "title": raw_sku.get("title") or raw_sku.get("name") or f"SKU {index}",
                    "price": str(raw_sku.get("price") or raw_sku.get("sale_price") or data.get("price") or "0"),
                    "stock": int(raw_sku.get("stock") or raw_sku.get("quantity") or 0),
                    "attributes": raw_sku.get("attributes") or {},
                    "image": raw_sku.get("image") or (images[0] if images else ""),
                }
            )
        if not normalized_skus:
            normalized_skus = build_mock_1688_detail(item_id=item_id, source_url=source_url)["skus"]
        price_ladder = data.get("price_ladder") or data.get("priceRanges") or [
            {"min_quantity": 1, "price": normalized_skus[0]["price"]}
        ]
        return {
            "item_id": item_id,
            "title": data.get("title") or f"1688 Item {item_id}",
            "main_image": images[0] if images else "",
            "images": images or [sku["image"] for sku in normalized_skus if sku.get("image")],
            "price": normalized_skus[0]["price"],
            "stock": sum(int(sku["stock"]) for sku in normalized_skus),
            "price_ladder": price_ladder,
            "attributes": {**attributes, "source_url": source_url},
            "skus": normalized_skus,
            "mocked": False,
        }

    def fetch_product_detail(self, item_id: str, source_url: str = "") -> dict[str, Any]:
        if not self._api_base_url() or not self._app_key() or not self._app_secret() or getattr(settings, "DEMO_MODE", False):
            return build_mock_1688_detail(item_id=item_id, source_url=source_url)

        try:
            payload = self._http_client().get(
                getattr(settings, "ALIBABA1688_DETAIL_PATH", "products/detail"),
                params={"item_id": item_id},
                headers={
                    "X-App-Key": self._app_key(),
                    "X-App-Secret": self._app_secret(),
                },
                scope=item_id,
            )
        except Exception:
            if getattr(settings, "DEMO_MODE", False):
                return build_mock_1688_detail(item_id=item_id, source_url=source_url)
            raise
        return self._normalize_detail(payload, item_id=item_id, source_url=source_url)

    def fetch_products(self, target_ids: list[str]) -> list[dict[str, Any]]:
        rows = []
        for item_id in target_ids:
            detail = self.fetch_product_detail(item_id=item_id)
            rows.append(
                {
                    "platform_product_id": detail["item_id"],
                    "title": detail["title"],
                    "images": detail["images"],
                    "attributes": {
                        **(detail.get("attributes") or {}),
                        "price_ladder": detail.get("price_ladder", []),
                    },
                    "price": detail["price"],
                    "stock": detail["stock"],
                }
            )
        return rows


def get_platform_client(platform: str) -> BasePlatformClient:
    normalized = (platform or "").strip().lower()
    supported = {"tiktok", "amazon", "1688", "shein"}
    if normalized not in supported:
        raise ValueError(f"Unsupported platform: {platform}")
    if normalized == "tiktok":
        return TikTokPlatformClient(platform=normalized)
    if normalized == "shein":
        return SheinPlatformClient(platform=normalized)
    if normalized == "1688":
        return Alibaba1688PlatformClient(platform=normalized)
    return BasePlatformClient(platform=normalized)
