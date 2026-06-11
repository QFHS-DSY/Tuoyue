from __future__ import annotations

import math
import time

from django.conf import settings
from django.core.cache import cache

try:
    from django_redis import get_redis_connection
except Exception:  # pragma: no cover - django_redis is part of runtime deps
    get_redis_connection = None


def _redis_connection():
    if get_redis_connection is None:
        return None
    try:
        return get_redis_connection("default")
    except Exception:
        return None


def _normalized_username(username: str) -> str:
    value = (username or "").strip().lower()
    return value or "unknown"


def _lock_seconds() -> int:
    return max(int(getattr(settings, "AUTH_LOGIN_FAIL_LOCK_SECONDS", 900)), 1)


def _max_attempts() -> int:
    return max(int(getattr(settings, "AUTH_LOGIN_FAIL_MAX_ATTEMPTS", 5)), 1)


def _failure_key(ip: str, username: str) -> str:
    prefix = str(getattr(settings, "AUTH_LOGIN_FAIL_PREFIX", "login_fail:"))
    return f"{prefix}{ip}:{_normalized_username(username)}"


def _lock_meta_key(failure_key: str) -> str:
    return f"{failure_key}:lock_until"


def get_login_lock_state(ip: str, username: str) -> tuple[bool, int]:
    failure_key = _failure_key(ip, username)
    conn = _redis_connection()
    if conn is not None:
        try:
            raw_count = conn.get(failure_key)
            if raw_count is None:
                return False, 0
            if int(raw_count) < _max_attempts():
                return False, 0
            ttl = int(conn.ttl(failure_key))
            if ttl <= 0:
                ttl = _lock_seconds()
                conn.expire(failure_key, ttl)
            return True, ttl
        except Exception:
            pass

    raw_count = cache.get(failure_key) or 0
    try:
        if int(raw_count) < _max_attempts():
            return False, 0
    except Exception:
        return False, 0

    lock_until = float(cache.get(_lock_meta_key(failure_key)) or 0)
    remaining = int(math.ceil(lock_until - time.time()))
    if remaining <= 0:
        cache.delete_many([failure_key, _lock_meta_key(failure_key)])
        return False, 0
    return True, remaining


def record_failed_login(ip: str, username: str) -> int:
    failure_key = _failure_key(ip, username)
    lock_seconds = _lock_seconds()
    conn = _redis_connection()
    if conn is not None:
        try:
            current = int(conn.incr(failure_key))
            conn.expire(failure_key, lock_seconds)
            return current
        except Exception:
            pass

    current = int(cache.get(failure_key) or 0) + 1
    cache.set(failure_key, current, timeout=lock_seconds)
    if current >= _max_attempts():
        cache.set(_lock_meta_key(failure_key), time.time() + lock_seconds, timeout=lock_seconds)
    return current


def clear_failed_login_state(ip: str, username: str) -> None:
    failure_key = _failure_key(ip, username)
    conn = _redis_connection()
    if conn is not None:
        try:
            conn.delete(failure_key)
        except Exception:
            pass
    cache.delete_many([failure_key, _lock_meta_key(failure_key)])
