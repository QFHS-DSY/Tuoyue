from __future__ import annotations

from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

from apps.core.models import PlatformToken
from apps.core.platform_clients import get_platform_client
from apps.core.services import build_expire_time


@shared_task(
    bind=True,
    name="apps.oauth.tasks.refresh_platform_token",
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def refresh_platform_token(self, token_id: int):
    token_obj = PlatformToken.objects.get(id=token_id)
    client = get_platform_client(token_obj.platform)
    refreshed = client.refresh_token(token_obj.refresh_token)
    token_obj.set_tokens(refreshed["access_token"], refreshed["refresh_token"])
    token_obj.expires_at = build_expire_time(int(refreshed.get("expires_in", 7200)))
    token_obj.save(update_fields=["access_token_encrypted", "refresh_token_encrypted", "expires_at", "updated_at"])
    token_obj.cache_tokens()
    return {"token_id": token_obj.id, "platform": token_obj.platform, "expires_at": token_obj.expires_at.isoformat()}


@shared_task(name="apps.oauth.tasks.refresh_expiring_platform_tokens")
def refresh_expiring_platform_tokens():
    lead_seconds = max(int(getattr(settings, "OAUTH_REFRESH_LEAD_SECONDS", 1800)), 60)
    threshold = timezone.now() + timedelta(seconds=lead_seconds)
    expiring_tokens = PlatformToken.objects.filter(expires_at__lte=threshold)
    queued = 0
    for token_obj in expiring_tokens.iterator():
        refresh_platform_token.delay(token_obj.id)
        queued += 1
    return {"queued": queued}
