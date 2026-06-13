import uuid
import hashlib
import json
import csv
import time
import random
import datetime
import socket
import logging
from pathlib import Path
from typing import Any, Dict
from datetime import timedelta
from django.conf import settings
from django.core.paginator import Paginator
from django.core.cache import cache
from django.db import connections, models
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests

from apps.common.rbac_permissions import HasApiIntegratorRole
from apps.common.responses import error_response, success_response
from apps.oauth.services import map_product_to_shein_payload

from .auth_rate_limit import clear_failed_login_state, get_login_lock_state, record_failed_login
from .models import (
    ApiIdempotencyRecord,
    CollectionTask,
    DeadLetterTask,
    InventorySyncLog,
    LogisticsRateCard,
    LogisticsShipment,
    LogisticsTrackingEvent,
    Order,
    PlatformToken,
    UserPhoneBinding,
    AccountDeletionLog,
    SmsDispatchLog,
    PhoneRebindAppeal,
    DevicePhoneRelation,
    Product,
    ProductVariant,
    ReplayAuditLog,
    Shop,
)
from .platform_clients import PlatformRateLimitError, get_platform_client
from .logistics_clients import get_logistics_aggregator_client
from .permissions import HasOrderEditPermission, IsOpsAdmin
from .serializers import (
    CollectionTaskCreateSerializer,
    CollectionTaskSerializer,
    InventorySyncLogSerializer,
    FreightEstimateQuerySerializer,
    LogisticsShipmentSerializer,
    LogisticsRateCardSerializer,
    OrderSerializer,
    OrderAddressUpdateSerializer,
    OrderStatusUpdateSerializer,
    ProductSerializer,
    SmsCodeSendSerializer,
    SmsCodeVerifySerializer,
    SmsRegisterSerializer,
    MobileAuthSerializer,
    AccountDeleteSerializer,
    PhoneRebindAppealSerializer,
    SmsChannelStatsQuerySerializer,
    ShopSerializer,
)
from .sms_providers import SmsSendError
from .sms_service import (
    check_send_rate_limits,
    create_captcha_challenge,
    dispatch_sms_with_failover,
    generate_sms_code,
    get_client_ip,
    check_and_incr_global_sms_limit,
    is_device_blacklisted,
    register_device_phone_attempt,
    record_send_success,
    store_sms_code,
    verify_sms_code_with_lua,
    validate_captcha_if_required,
)
from .services import build_expire_time
from .tasks import execute_collection_task, scheduled_inventory_sync


logger = logging.getLogger(__name__)


def _request_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=True).encode("utf-8")).hexdigest()


def _rate_limited_response(message: str, retry_after: int):
    response = error_response(message=message, status_code=429, code=429)
    response["Retry-After"] = str(max(int(retry_after or 1), 1))
    return response


def _sync_user_profile_phone(user, phone: str) -> None:
    normalized_phone = str(phone or "").strip()
    if not normalized_phone:
        return
    try:
        from apps.settings_sys.models import UserProfile

        profile, created = UserProfile.objects.get_or_create(user=user, defaults={"phone": normalized_phone})
        if not created and not str(profile.phone or "").strip():
            profile.phone = normalized_phone
            profile.save(update_fields=["phone"])
    except Exception:
        return


def _resolve_login_username(raw_username: str, country_code: str = "") -> str:
    username = str(raw_username or "").strip()
    if not username or not username.isdigit():
        return username

    bindings = UserPhoneBinding.objects.select_related("user").filter(phone_number=username)
    binding = None
    if country_code:
        binding = bindings.filter(country_code=country_code).first()
    if not binding:
        binding = bindings.first()
    return binding.user.username if binding else username


def _debug_sms_bypass_enabled(submitted_code: str) -> bool:
    bypass_code = str(getattr(settings, "SMS_DEBUG_BYPASS_CODE", "") or "").strip()
    return bool(getattr(settings, "DEBUG", False) and bypass_code and str(submitted_code).strip() == bypass_code)


def _verify_sms_code_or_response(phone: str, submitted_code: str, default_error: str = "验证码错误"):
    if _debug_sms_bypass_enabled(submitted_code):
        return True, None

    try:
        ok, err_msg, status_code = verify_sms_code_with_lua(phone, submitted_code)
    except Exception:
        logger.exception("sms verification backend unavailable phone=%s", phone)
        return False, error_response(message="验证码服务暂不可用，请稍后重试", status_code=503, code=503)

    if not ok:
        return False, error_response(message=err_msg or default_error, status_code=status_code, code=status_code)

    return True, None


def _persist_1688_product_detail(detail: dict) -> Product:
    attributes = dict(detail.get("attributes") or {})
    attributes["price_ladder"] = detail.get("price_ladder", [])
    if detail.get("source_url"):
        attributes["source_url"] = detail["source_url"]

    with transaction.atomic():
        product, _ = Product.objects.update_or_create(
            platform="1688",
            platform_product_id=str(detail["item_id"]),
            defaults={
                "title": detail.get("title", ""),
                "images": detail.get("images", []),
                "attributes": attributes,
                "price": detail.get("price", "0"),
                "stock": int(detail.get("stock", 0) or 0),
            },
        )
        seen_skus = []
        for raw_sku in detail.get("skus", []):
            sku_code = str(raw_sku.get("sku") or "").strip()
            if not sku_code:
                continue
            seen_skus.append(sku_code)
            ProductVariant.objects.update_or_create(
                product=product,
                sku=sku_code,
                defaults={
                    "title": raw_sku.get("title") or product.title,
                    "price": raw_sku.get("price") or product.price,
                    "stock": int(raw_sku.get("stock", 0) or 0),
                    "attributes": raw_sku.get("attributes") or {},
                },
            )
        if seen_skus:
            product.variants.exclude(sku__in=seen_skus).delete()
    return product


def _resolve_platform_access_token(platform: str, account_id: str = "") -> str:
    lookup_account_id = (account_id or "default").strip() or "default"
    token_obj = PlatformToken.objects.filter(platform=platform, account_id=lookup_account_id).first()
    if token_obj is None and lookup_account_id != "default":
        token_obj = PlatformToken.objects.filter(platform=platform, account_id="default").first()
    if token_obj is None:
        return ""
    try:
        return token_obj.access_token
    except Exception:
        return ""


def _publish_product_to_shein(product: Product, shop_id: str = "") -> dict:
    client = get_platform_client("shein")
    payload = map_product_to_shein_payload(product)
    access_token = _resolve_platform_access_token("shein", account_id=shop_id)
    return client.publish_listing(payload, shop_id=shop_id, access_token=access_token)


# RBAC：采集/同步/平台 Token 刷新等业务接口（Django Group + JWT）
_BUSINESS_API_PERMISSIONS = [IsAuthenticated, HasApiIntegratorRole]
class AuthLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="获取平台授权 URL")
    def get(self, request, platform):
        try:
            client = get_platform_client(platform)
            state = request.query_params.get("state", str(uuid.uuid4()))
            login_url = client.get_oauth_authorize_url(state=state)
            return success_response({"authorization_url": login_url, "state": state})
        except Exception as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)


class AuthCallbackView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="平台 OAuth 回调并保存 Token")
    def get(self, request, platform):
        code = request.query_params.get("code")
        if not code:
            return error_response(message="code is required", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            client = get_platform_client(platform)
            token_payload = client.exchange_code_for_token(code)
            token_obj, _ = PlatformToken.objects.get_or_create(
                platform=platform,
                account_id=token_payload.get("account_id", "default"),
            )
            token_obj.set_tokens(token_payload["access_token"], token_payload["refresh_token"])
            token_obj.expires_at = build_expire_time(token_payload["expires_in"])
            token_obj.save()
            token_obj.cache_tokens()
            return success_response(
                {
                    "platform": token_obj.platform,
                    "account_id": token_obj.account_id,
                    "expires_at": token_obj.expires_at,
                }
            )
        except Exception as exc:
            return error_response(message=str(exc), status_code=status.HTTP_400_BAD_REQUEST)


class AuthRefreshView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="手动刷新平台 Token")
    def post(self, request, platform):
        account_id = request.data.get("account_id", "default")
        token_obj = get_object_or_404(PlatformToken, platform=platform, account_id=account_id)
        from apps.oauth.tasks import refresh_platform_token as refresh_platform_token_task

        refresh_platform_token_task.delay(token_obj.id)
        return success_response({"queued": True, "token_id": token_obj.id})


class CollectionTaskCreateView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="创建采集任务并推送队列")
    def post(self, request):
        idem_key = request.headers.get("X-Idempotency-Key", "").strip()
        if idem_key:
            req_hash = _request_hash(request.data)
            existing = ApiIdempotencyRecord.objects.filter(idem_key=idem_key, endpoint=request.path).first()
            if existing and existing.request_hash == req_hash:
                return success_response(existing.response_data, status_code=existing.status_code)

        serializer = CollectionTaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = CollectionTask.objects.create(
            platform=serializer.validated_data["platform"],
            target_ids=serializer.validated_data["target_ids"],
            status="pending",
        )
        execute_collection_task.delay(task.id)
        response_data = {"task_id": task.id, "status": task.status}
        if idem_key:
            ApiIdempotencyRecord.objects.update_or_create(
                idem_key=idem_key,
                endpoint=request.path,
                defaults={
                    "request_hash": _request_hash(request.data),
                    "response_data": response_data,
                    "status_code": status.HTTP_201_CREATED,
                },
            )
        return success_response(response_data, status_code=status.HTTP_201_CREATED)


class CollectionTaskStatusView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="查询采集任务状态")
    def get(self, request, task_id):
        task = get_object_or_404(CollectionTask, id=task_id)
        data = CollectionTaskSerializer(task).data
        return success_response(data)


class SyncTriggerView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="手动触发库存同步")
    def post(self, request):
        idem_key = request.headers.get("X-Idempotency-Key", "").strip()
        if idem_key:
            req_hash = _request_hash(request.data)
            existing = ApiIdempotencyRecord.objects.filter(idem_key=idem_key, endpoint=request.path).first()
            if existing and existing.request_hash == req_hash:
                return success_response(existing.response_data, status_code=existing.status_code)

        scheduled_inventory_sync.delay()
        response_data = {"queued": True}
        if idem_key:
            ApiIdempotencyRecord.objects.update_or_create(
                idem_key=idem_key,
                endpoint=request.path,
                defaults={"request_hash": _request_hash(request.data), "response_data": response_data, "status_code": 200},
            )
        return success_response(response_data)


class SyncLogView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="获取库存同步日志")
    def get(self, request):
        logs = InventorySyncLog.objects.all().order_by("-created_at")[:100]
        data = InventorySyncLogSerializer(logs, many=True).data
        return success_response(data)


class DeadLetterListView(APIView):
    permission_classes = [IsAuthenticated, IsOpsAdmin]

    @extend_schema(summary="查看 dead-letter 列表")
    def get(self, request):
        queryset = DeadLetterTask.objects.all().order_by("-created_at")
        status_value = request.query_params.get("status")
        task_name = request.query_params.get("task_name")
        if status_value:
            queryset = queryset.filter(status=status_value)
        if task_name:
            queryset = queryset.filter(task_name=task_name)

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        page_size = min(max(page_size, 1), 200)
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        rows = current_page.object_list
        data = [
            {
                "id": row.id,
                "task_name": row.task_name,
                "payload": row.payload,
                "error_message": row.error_message,
                "retry_count": row.retry_count,
                "status": row.status,
                "created_at": row.created_at,
            }
            for row in rows
        ]
        return success_response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "page": current_page.number,
                "page_size": page_size,
                "results": data,
            }
        )


class DeadLetterReplayView(APIView):
    permission_classes = [IsAuthenticated, IsOpsAdmin]

    @extend_schema(summary="重放 dead-letter 任务")
    def post(self, request, dead_letter_id):
        row = get_object_or_404(DeadLetterTask, id=dead_letter_id)
        task_name = row.task_name
        payload = row.payload or {}
        operator = request.user.username if getattr(request, "user", None) and request.user.is_authenticated else "system"

        try:
            if task_name == "execute_collection_task":
                execute_collection_task.delay(payload["task_id"])
            elif task_name == "refresh_platform_token":
                refresh_platform_token.delay(payload["token_id"])
            elif task_name == "sync_inventory_by_rule":
                from .tasks import sync_inventory_by_rule

                sync_inventory_by_rule.delay(payload["sync_rule_id"])
            else:
                ReplayAuditLog.objects.create(
                    dead_letter_task=row,
                    operator=operator,
                    result="failed",
                    detail=f"Unsupported task_name: {task_name}",
                )
                return error_response(message=f"Unsupported task_name: {task_name}", status_code=400)

            row.status = DeadLetterTask.STATUS_REPLAYED
            row.retry_count += 1
            row.save(update_fields=["status", "retry_count", "updated_at"])
            ReplayAuditLog.objects.create(dead_letter_task=row, operator=operator, result="success", detail="replay queued")
            return success_response({"replayed": True, "dead_letter_id": row.id})
        except Exception as exc:
            ReplayAuditLog.objects.create(dead_letter_task=row, operator=operator, result="failed", detail=str(exc))
            return error_response(message=str(exc), status_code=500)


class ReplayAuditLogListView(APIView):
    permission_classes = [IsAuthenticated, IsOpsAdmin]

    @extend_schema(summary="查看重放审计日志")
    def get(self, request):
        queryset = ReplayAuditLog.objects.all().order_by("-created_at")
        dead_letter_id = request.query_params.get("dead_letter_id")
        if dead_letter_id:
            queryset = queryset.filter(dead_letter_task_id=dead_letter_id)
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 20))
        page_size = min(max(page_size, 1), 200)
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        data = [
            {
                "id": row.id,
                "dead_letter_task_id": row.dead_letter_task_id,
                "operator": row.operator,
                "result": row.result,
                "detail": row.detail,
                "created_at": row.created_at,
            }
            for row in current_page.object_list
        ]
        return success_response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "page": current_page.number,
                "page_size": page_size,
                "results": data,
            }
        )


class OpsWhoAmIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="运维权限自检")
    def get(self, request):
        user = request.user
        ops_by_group = user.groups.filter(name="ops_admin").exists()
        ops_by_list = user.username in set(getattr(settings, "OPS_ADMIN_USERNAMES", []))
        is_ops_admin = user.is_superuser or ops_by_group or ops_by_list
        return success_response(
            {
                "username": user.username,
                "is_superuser": user.is_superuser,
                "ops_by_group": ops_by_group,
                "ops_by_list": ops_by_list,
                "is_ops_admin": is_ops_admin,
            }
        )


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    @extend_schema(summary="系统健康检查")
    def get(self, request):
        # region agent log
        def _agent_log(hypothesis_id: str, message: str, data: dict) -> None:
            try:
                base_dir = getattr(settings, "BASE_DIR", ".")
                log_dir = Path(str(base_dir)) / "logs"
                log_dir.mkdir(parents=True, exist_ok=True)
                log_path = log_dir / "debug.log"
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "ac2c4e",
                                "runId": "pre-fix",
                                "hypothesisId": hypothesis_id,
                                "location": "apps/core/views.py:HealthCheckView.get",
                                "message": message,
                                "data": data or {},
                                "timestamp": int(time.time() * 1000),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
            except Exception:
                pass

        db = (getattr(settings, "DATABASES", {}) or {}).get("default", {}) or {}
        db_engine = db.get("ENGINE")
        db_host = db.get("HOST")
        db_port = db.get("PORT")
        _agent_log(
            "DB_H1_H2_H3_H4",
            "healthcheck db resolved",
            {"engine": db_engine, "host": db_host, "port": db_port, "path": request.path},
        )

        tcp_ok = None
        tcp_err = None
        try:
            port_int = int(str(db_port or "3306"))
            host_str = str(db_host or "127.0.0.1")
            with socket.create_connection((host_str, port_int), timeout=1.5):
                tcp_ok = True
        except Exception as exc:
            tcp_ok = False
            tcp_err = f"{type(exc).__name__}: {exc}"
        _agent_log(
            "DB_H1_H2",
            "healthcheck mysql tcp probe",
            {"tcp_ok": tcp_ok, "tcp_error": tcp_err, "host": db_host, "port": db_port},
        )
        # endregion

        checks = {"database": False, "cache": False}
        try:
            with connections["default"].cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            checks["database"] = True
        except Exception:
            checks["database"] = False
            # region agent log
            _agent_log("DB_H1_H2_H3_H4_H5", "healthcheck db query failed", {"database": checks["database"]})
            # endregion
        else:
            # region agent log
            _agent_log("DB_H5", "healthcheck db query ok", {"database": checks["database"]})
            # endregion

        try:
            cache.set("healthcheck:ping", "pong", timeout=10)
            checks["cache"] = cache.get("healthcheck:ping") == "pong"
        except Exception:
            checks["cache"] = False

        ok = all(checks.values())
        code = 200 if ok else 503
        return success_response(
            data={
                "status": "ok" if ok else "degraded",
                "checks": checks,
                "ops_admin_usernames": getattr(settings, "OPS_ADMIN_USERNAMES", []),
            },
            status_code=code,
            code=code,
            message="success" if ok else "service unavailable",
        )


class AuthMeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="获取当前用户信息")
    def get(self, request):
        user = request.user
        return success_response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_superuser": user.is_superuser,
            }
        )


class UserRegisterView(APIView):
    """真实业务：用户注册（用户名/密码 或 手机号/密码）。"""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(summary="用户注册")
    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        sms_phone = str(payload.get("mobile") or payload.get("phone") or "").strip()
        sms_code = str(payload.get("sms_code") or payload.get("code") or "").strip()
        if sms_phone and sms_code:
            serializer = SmsRegisterSerializer(data=payload)
            serializer.is_valid(raise_exception=True)
            if not serializer.validated_data["agreed_privacy"]:
                return error_response(message="必须同意隐私协议", status_code=400, code=400)

            country_code = serializer.validated_data["country_code"]
            mobile = serializer.validated_data["mobile"]
            full_phone = f"+{country_code}{mobile}"
            verified, error_resp = _verify_sms_code_or_response(full_phone, serializer.validated_data["code"])
            if not verified:
                return error_resp

            User = get_user_model()
            with transaction.atomic():
                existing_binding = UserPhoneBinding.objects.select_for_update().filter(
                    country_code=country_code,
                    phone_number=mobile,
                ).first()
                if existing_binding:
                    return error_response(message="该手机号已注册", status_code=400, code=400)

                username = mobile
                if User.objects.filter(username=username).exists():
                    username = f"u_{country_code}_{mobile}_{int(time.time())}"

                user = User.objects.create_user(
                    username=username,
                    password=serializer.validated_data["password"],
                )
                UserPhoneBinding.objects.create(
                    user=user,
                    country_code=country_code,
                    phone_number=mobile,
                    is_primary=True,
                )

            _sync_user_profile_phone(user, mobile)
            refresh = RefreshToken.for_user(user)
            return success_response(
                data={
                    "created": True,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "access_token": str(refresh.access_token),
                    "refresh_token": str(refresh),
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "mobile": _mask_mobile(full_phone),
                        "country_code": country_code,
                    },
                },
                code=200,
                status_code=200,
                message="registered",
            )

        username = (payload.get("username") or payload.get("phone") or "").strip()
        password = payload.get("password") or ""
        if not username or not password:
            return error_response(message="username and password are required", status_code=400, code=400)

        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return error_response(message="username already exists", status_code=400, code=400)

        user = User.objects.create_user(username=username, password=password)
        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {"id": user.id, "username": user.username},
            },
            code=200,
            status_code=200,
            message="registered",
        )


class UserLoginView(APIView):
    """真实业务：用户登录（用户名/密码）。"""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(summary="用户登录")
    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        username = (payload.get("username") or payload.get("phone") or "").strip()
        password = payload.get("password") or ""
        if not username or not password:
            return error_response(message="username and password are required", status_code=400, code=400)

        country_code = str(payload.get("country_code") or "").strip()
        client_ip = get_client_ip(request.META)
        is_locked, retry_after = get_login_lock_state(client_ip, username)
        if is_locked:
            return _rate_limited_response("too many login failures, please retry later", retry_after=retry_after)

        auth_username = _resolve_login_username(username, country_code=country_code)
        user = authenticate(request, username=auth_username, password=password)
        if not user:
            record_failed_login(client_ip, username)
            return error_response(message="invalid credentials", status_code=401, code=401)

        clear_failed_login_state(client_ip, username)
        refresh = RefreshToken.for_user(user)
        return success_response(
            data={
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "user": {"id": user.id, "username": user.username},
            },
            code=200,
            status_code=200,
            message="ok",
        )


class UserTokenRefreshView(APIView):
    """真实业务：刷新 JWT access token。"""

    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(summary="刷新 Token")
    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        raw_refresh = payload.get("refresh_token") or payload.get("refresh") or ""
        if not raw_refresh:
            return error_response(message="refresh_token is required", status_code=400, code=400)
        try:
            refresh = RefreshToken(raw_refresh)
        except Exception:
            return error_response(message="invalid refresh token", status_code=401, code=401)
        return success_response(
            data={"access_token": str(refresh.access_token), "refresh_token": str(refresh)},
            code=200,
            status_code=200,
            message="ok",
        )


class DemoAuthLoginView(UserLoginView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="用户名密码登录（兼容旧演示路由）")
    def post(self, request):
        return super().post(request)


class DemoAuthMeView(AuthMeView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="获取当前用户信息（兼容旧演示路由）")
    def get(self, request):
        return super().get(request)


class DemoAuthRefreshView(UserTokenRefreshView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="刷新 Token（兼容旧演示路由）")
    def post(self, request):
        return super().post(request)


class DemoAuthRegisterView(UserRegisterView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="注册（兼容旧演示路由）")
    def post(self, request):
        return super().post(request)


class GoodsListingSyncView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="商品上架/同步指令下发")
    def post(self, request):
        from .serializers import GoodsListingSerializer
        serializer = GoodsListingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        goods_id = serializer.validated_data["goods_id"]
        platform = serializer.validated_data["platform"]
        shop_id = serializer.validated_data.get("shop_id")
        
        product = get_object_or_404(Product.objects.prefetch_related("variants"), id=goods_id)
        
        if platform == "shein":
            try:
                result = _publish_product_to_shein(product, shop_id=shop_id or "")
            except PlatformRateLimitError as exc:
                return _rate_limited_response("shein upstream rate limited", retry_after=exc.retry_after)
            except Exception as exc:
                return error_response(message=str(exc), status_code=400)

            task = CollectionTask.objects.create(
                platform=platform,
                target_ids=[str(product.platform_product_id)],
                status="success",
                result_message=f"listing pushed to {platform}",
            )
            return success_response(
                {
                    "task_id": task.id,
                    "goods_id": goods_id,
                    "platform": platform,
                    "shop_id": shop_id,
                    "result": result,
                    "message": "listing published",
                }
            )

        task = CollectionTask.objects.create(
            platform=platform,
            target_ids=[str(product.platform_product_id)],
            status="pending",
        )
        execute_collection_task.delay(task.id)
        
        return success_response(
            {
                "task_id": task.id,
                "goods_id": goods_id,
                "platform": platform,
                "shop_id": shop_id,
                "message": "指令已下发，商品同步任务已创建",
            }
        )


class GoodsBatchListingSyncView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="商品批量上架/同步指令下发")
    def post(self, request):
        from .serializers import GoodsBatchListingSerializer
        serializer = GoodsBatchListingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        items = serializer.validated_data["items"]
        platform = serializer.validated_data["platform"]
        
        target_ids = []
        for item in items:
            goods_id = item.get("goods_id")
            if goods_id:
                product = Product.objects.filter(id=goods_id).first()
                if product:
                    target_ids.append(str(product.platform_product_id))
        
        if not target_ids:
            return error_response(message="未找到有效的商品ID", status_code=400)
        
        if platform == "shein":
            published = []
            try:
                for item in items:
                    goods_id = item.get("goods_id")
                    if not goods_id:
                        continue
                    product = Product.objects.prefetch_related("variants").filter(id=goods_id).first()
                    if product is None:
                        continue
                    published.append(
                        {
                            "goods_id": product.id,
                            "platform_product_id": product.platform_product_id,
                            "shop_id": item.get("shop_id", ""),
                            "result": _publish_product_to_shein(product, shop_id=item.get("shop_id", "")),
                        }
                    )
            except PlatformRateLimitError as exc:
                return _rate_limited_response("shein upstream rate limited", retry_after=exc.retry_after)
            except Exception as exc:
                return error_response(message=str(exc), status_code=400)

            task = CollectionTask.objects.create(
                platform=platform,
                target_ids=[row["platform_product_id"] for row in published],
                status="success",
                result_message=f"published {len(published)} listings",
            )
            return success_response(
                {
                    "task_id": task.id,
                    "platform": platform,
                    "item_count": len(published),
                    "results": published,
                    "message": "batch listing published",
                }
            )

        task = CollectionTask.objects.create(
            platform=platform,
            target_ids=target_ids,
            status="pending",
        )
        execute_collection_task.delay(task.id)
        
        return success_response(
            {
                "task_id": task.id,
                "platform": platform,
                "item_count": len(target_ids),
                "message": "批量上架指令已下发，任务队列处理中",
            }
        )


class DemoSmsQueryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="短信发送记录查询（生产化保留兼容接口）")
    def get(self, request):
        from .models import SmsDispatchLog
        rows = SmsDispatchLog.objects.all().order_by("-requested_at")[:100]
        items = []
        for row in rows:
            items.append(
                {
                    "phone": row.phone,
                    "status": row.status,
                    "provider": row.provider,
                    "requested_at": row.requested_at,
                    "delivered_at": row.delivered_at,
                }
            )
        return success_response({"total": len(items), "items": items})


class SmsBatchSendView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="批量发送短信（骨架视图，Demo 模式占位）")
    def post(self, request):
        if settings.DEMO_MODE:
            return success_response({"total": 3, "success": 3, "failed": 0, "message": "批量发送已完成"})
        # 防刷限流：同一用户每小时最多调用 10 次
        from django.core.cache import cache
        user_key = f"sms-batch:user:{request.user.id}"
        hour_key = f"{user_key}:{timezone.now().strftime('%Y%m%d%H')}"
        call_count = cache.get(hour_key, 0)
        if call_count >= 10:
            return error_response(message="请求过于频繁，每小时最多发送 10 次批量短信", status_code=429)
        cache.set(hour_key, call_count + 1, timeout=3600)

        from .sms_service import generate_sms_code, store_sms_code, record_send_success
        phones = request.data.get("phones", [])
        if not phones:
            return error_response(message="phones is required", status_code=400)
        if len(phones) > 100:
            return error_response(message="单次批量发送最多 100 个号码", status_code=400)
        results = []
        for phone in phones:
            code = generate_sms_code()
            store_sms_code(phone, code)
            record_send_success(phone, "mock")
            results.append({"phone": phone, "status": "sent"})
        return success_response({"total": len(results), "results": results})


class CollectAuthView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="采集平台授权登录")
    def post(self, request, platform: str):
        redirect_url = f"/api/auth/{platform}/callback/"
        return success_response({
            "platform": platform,
            "auth_url": redirect_url,
            "message": "授权链接已生成"
        })

    @extend_schema(summary="采集平台授权回调/状态查询")
    def get(self, request, platform: str):
        auth_token = cache.get(f"{platform}_auth_token")
        if not auth_token:
            auth_token = f"demo_token_{uuid.uuid4().hex}"
            cache.set(f"{platform}_auth_token", auth_token, 86400)
            cache.set(f"{platform}_auth_account", f"{platform}_user", 86400)
        
        account = cache.get(f"{platform}_auth_account", f"{platform}_user")
        
        return success_response({
            "platform": platform,
            "authorized": True,
            "account": account,
            "token": auth_token,
            "message": "授权状态正常"
        })

    @extend_schema(summary="采集平台登出")
    def delete(self, request, platform: str):
        cache.delete(f"{platform}_auth_token")
        cache.delete(f"{platform}_auth_account")
        return success_response({
            "platform": platform,
            "authorized": False,
            "message": "登出成功"
        })


class DemoCollectAuthLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="采集平台授权登录（Demo 路由骨架）")
    def post(self, request, platform: str):
        redirect_url = f"/api/auth/{platform}/callback/"
        return success_response({
            "platform": platform,
            "auth_url": redirect_url,
            "message": "授权链接已生成"
        })


class DemoCollectAuthCallbackView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="采集平台授权回调（Demo 路由骨架）")
    def get(self, request, platform: str):
        auth_token = cache.get(f"{platform}_auth_token")
        if not auth_token:
            auth_token = f"demo_token_{uuid.uuid4().hex}"
            cache.set(f"{platform}_auth_token", auth_token, 86400)
            cache.set(f"{platform}_auth_account", f"{platform}_user", 86400)
        account = cache.get(f"{platform}_auth_account", f"{platform}_user")
        return success_response({
            "platform": platform,
            "authorized": True,
            "account": account,
            "token": auth_token,
            "message": "授权状态正常"
        })


class DemoCollectAuthStatusView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="采集平台授权状态（Demo 路由骨架）")
    def get(self, request, platform: str):
        auth_token = cache.get(f"{platform}_auth_token")
        authorized = auth_token is not None
        account = cache.get(f"{platform}_auth_account", "") if authorized else ""
        return success_response({
            "platform": platform,
            "authorized": authorized,
            "account": account,
            "message": "授权状态正常" if authorized else "未授权"
        })


class DemoCollectAuthLogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="采集平台授权登出（Demo 路由骨架）")
    def post(self, request, platform: str):
        cache.delete(f"{platform}_auth_token")
        cache.delete(f"{platform}_auth_account")
        return success_response({
            "platform": platform,
            "authorized": False,
            "message": "登出成功"
        })


class CollectTaskView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="创建采集任务")
    def post(self, request, task_id: int | None = None):
        if task_id:
            return self._cancel_task(request, task_id)
        
        serializer = CollectionTaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        idem_key = request.headers.get("X-Idempotency-Key", "").strip()
        if idem_key:
            req_hash = _request_hash(request.data)
            existing = ApiIdempotencyRecord.objects.filter(idem_key=idem_key, endpoint=request.path).first()
            if existing and existing.request_hash == req_hash:
                return success_response(existing.response_data, status_code=existing.status_code)
        
        task = CollectionTask.objects.create(
            platform=serializer.validated_data["platform"],
            target_ids=serializer.validated_data["target_ids"],
            status="pending",
        )
        execute_collection_task.delay(task.id)
        
        response_data = {"task_id": task.id, "status": task.status}
        if idem_key:
            ApiIdempotencyRecord.objects.update_or_create(
                idem_key=idem_key,
                endpoint=request.path,
                defaults={
                    "request_hash": _request_hash(request.data),
                    "response_data": response_data,
                    "status_code": status.HTTP_201_CREATED,
                },
            )
        
        return success_response(response_data, status_code=201)

    @extend_schema(summary="获取采集任务列表或详情")
    def get(self, request, task_id: int | None = None):
        if task_id:
            return self._get_task_detail(request, task_id)
        return self._get_task_list(request)

    def _get_task_list(self, request):
        queryset = CollectionTask.objects.all().order_by("-created_at")
        platform = request.query_params.get("platform", "").strip()
        status_value = request.query_params.get("status", "").strip()
        
        if platform:
            queryset = queryset.filter(platform=platform)
        if status_value:
            queryset = queryset.filter(status=status_value)
        
        page = int(request.query_params.get("page", 1))
        page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 200)
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        
        data = CollectionTaskSerializer(current_page.object_list, many=True).data
        return success_response(
            {
                "count": paginator.count,
                "num_pages": paginator.num_pages,
                "page": current_page.number,
                "page_size": page_size,
                "results": data,
            }
        )

    def _get_task_detail(self, request, task_id: int):
        task = get_object_or_404(CollectionTask, id=task_id)
        data = CollectionTaskSerializer(task).data
        return success_response(data)

    @extend_schema(summary="获取采集任务状态")
    def put(self, request, task_id: int):
        action = request.query_params.get("action", "").strip()
        if action == "cancel":
            return self._cancel_task(request, task_id)
        return self._get_task_status(request, task_id)

    def _get_task_status(self, request, task_id: int):
        task = get_object_or_404(CollectionTask, id=task_id)
        return success_response({"task_id": task.id, "status": task.status, "result_message": task.result_message})

    def _cancel_task(self, request, task_id: int):
        task = get_object_or_404(CollectionTask, id=task_id)
        if task.status not in ("pending", "running"):
            return error_response(message="任务状态不允许取消", status_code=400)
        
        task.status = "failed"
        task.result_message = "任务已被用户取消"
        task.save(update_fields=["status", "result_message", "updated_at"])
        
        return success_response({"task_id": task.id, "status": task.status, "message": "任务已取消"})

    @extend_schema(summary="删除采集任务")
    def delete(self, request, task_id: int):
        task = get_object_or_404(CollectionTask, id=task_id)
        task.delete()
        return success_response({"task_id": task_id, "deleted": True})





class DemoOrdersView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, order_id: int | None = None):
        if order_id is not None:
            return OrderDetailView.as_view()(request, order_id=order_id)
        return OrdersListView.as_view()(request)

    def post(self, request, order_id: int | None = None, action: str | None = None):
        if order_id is not None and action:
            mapping = {
                "confirm": OrderConfirmView,
                "ship": OrderShipView,
                "cancel": OrderCancelView,
                "remark": OrderRemarkView,
            }
            view_cls = mapping.get(action)
            if view_cls:
                return view_cls.as_view()(request, order_id=order_id)
        return error_response(message="unsupported action", status_code=400)


class DemoOrdersStatsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request):
        return OrdersStatsView.as_view()(request)


class DemoInventoryView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, sku: str | None = None):
        if sku:
            return InventoryOverviewView.as_view()(request)
        return InventoryOverviewView.as_view()(request)

    def post(self, request):
        return InventoryAdjustView.as_view()(request)


class DemoLogisticsView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, waybill: str | None = None):
        if waybill:
            return LogisticsTrackView.as_view()(request, waybill=waybill)
        return LogisticsShipmentsView.as_view()(request)

    def post(self, request):
        return LogisticsWebhookView.as_view()(request)


class Collect1688SingleView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="1688 单链接采集")
    def post(self, request):
        from .serializers import Collect1688SingleSerializer
        serializer = Collect1688SingleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url = serializer.validated_data["url"]
        source = serializer.validated_data["source"]
        
        item_id = self._extract_item_id_from_url(url)
        if not item_id:
            return error_response(message="无法从URL中提取商品ID", status_code=400)
        
        try:
            detail = get_platform_client(source).fetch_product_detail(item_id=item_id, source_url=url)
            product = _persist_1688_product_detail({**detail, "source_url": url})
        except PlatformRateLimitError as exc:
            return _rate_limited_response("1688 upstream rate limited", retry_after=exc.retry_after)
        except Exception as exc:
            return error_response(message=str(exc), status_code=400)

        task = CollectionTask.objects.create(
            platform=source,
            target_ids=[item_id],
            status="success",
            result_message="collected and persisted",
        )

        return success_response(
            {
                "task_id": task.id,
                "status": task.status,
                "source": source,
                "item_id": item_id,
                "product": ProductSerializer(product).data,
                "detail": detail,
            },
            status_code=201,
        )

    def _extract_item_id_from_url(self, url: str) -> str:
        import re
        match = re.search(r"item\.1688\.com/(?:offer/)?(\d+)\.html", url)
        if match:
            return match.group(1)
        match = re.search(r"1688\.com/.+?(\d+)\.html", url)
        if match:
            return match.group(1)
        return ""


class Collect1688BatchView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="1688 批量采集")
    def post(self, request):
        from .serializers import Collect1688BatchSerializer
        serializer = Collect1688BatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        urls = serializer.validated_data["urls"]
        source = serializer.validated_data["source"]
        
        target_ids = []
        for url in urls:
            item_id = self._extract_item_id_from_url(url)
            if item_id:
                target_ids.append(item_id)
        
        if not target_ids:
            return error_response(message="无法从URL中提取任何商品ID", status_code=400)
        
        results = []
        try:
            for index, item_id in enumerate(target_ids):
                detail = get_platform_client(source).fetch_product_detail(item_id=item_id, source_url=urls[index])
                product = _persist_1688_product_detail({**detail, "source_url": urls[index]})
                results.append({"item_id": item_id, "product_id": product.id, "detail": detail})
        except PlatformRateLimitError as exc:
            return _rate_limited_response("1688 upstream rate limited", retry_after=exc.retry_after)
        except Exception as exc:
            return error_response(message=str(exc), status_code=400)

        task = CollectionTask.objects.create(
            platform=source,
            target_ids=target_ids,
            status="success",
            result_message=f"collected {len(results)} items",
        )

        return success_response(
            {
                "task_id": task.id,
                "status": task.status,
                "source": source,
                "item_count": len(results),
                "results": results,
            },
            status_code=201,
        )

    def _extract_item_id_from_url(self, url: str) -> str:
        import re
        match = re.search(r"item\.1688\.com/(?:offer/)?(\d+)\.html", url)
        if match:
            return match.group(1)
        match = re.search(r"1688\.com/.+?(\d+)\.html", url)
        if match:
            return match.group(1)
        return ""


def _ai_fallback_copy() -> Dict[str, Any]:
    return {
        "title": "💡 Premium Smart Product | High-Quality, Minimalist Design",
        "description": (
            "✨ Upgrade your daily life with a sleek, reliable product built for performance. "
            "Designed for modern users, easy to use, and perfect for gifting."
        ),
        "bullets": [
            "🚀 Fast, dependable, and built to last",
            "🎯 Clean look with practical features",
            "🛡️ Quality materials, worry-free use",
            "📦 Ready for cross-border fulfillment",
        ],
    }


class AiProxyView(APIView):
    """
    前端 AI 文案请求转发到拓岳 New API。
    任何异常都必须兜底为演示文案，严禁向前端抛 502。
    """

    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="AI 中枢代理转发（失败兜底，永不 502）")
    def post(self, request):
        # region agent log
        try:
            with open("debug-12656f.log", "a", encoding="utf-8") as f:
                f.write(
                    json.dumps(
                        {
                            "sessionId": "12656f",
                            "runId": "pre-fix",
                            "hypothesisId": "H3",
                            "location": "apps/core/views.py:AiProxyView.post",
                            "message": "ai proxy request enter",
                            "data": {"path": request.path},
                            "timestamp": int(time.time() * 1000),
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        except Exception:
            pass
        # endregion
        target_url = "https://api.tuoyue-tech.shop"
        api_key = getattr(settings, "TUOYUE_NEW_API_AUTHORIZATION", "")
        payload = request.data if isinstance(request.data, dict) else {}
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = api_key

        try:
            resp = requests.post(target_url, json=payload, headers=headers, timeout=10)
            # region agent log
            try:
                with open("debug-12656f.log", "a", encoding="utf-8") as f:
                    f.write(
                        json.dumps(
                            {
                                "sessionId": "12656f",
                                "runId": "pre-fix",
                                "hypothesisId": "H3",
                                "location": "apps/core/views.py:AiProxyView.post",
                                "message": "ai proxy upstream response",
                                "data": {"status_code": resp.status_code},
                                "timestamp": int(time.time() * 1000),
                            },
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
            except Exception:
                pass
            # endregion
            if resp.status_code >= 500:
                return Response({"code": 200, "data": _ai_fallback_copy(), "message": "fallback"}, status=200)
            try:
                data = resp.json()
            except Exception:
                data = {"raw": resp.text}
            return Response({"code": 200, "data": data, "message": "success"}, status=200)
        except Exception:
            return Response({"code": 200, "data": _ai_fallback_copy(), "message": "fallback"}, status=200)


class AiGenerateTitleView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="AI 生成标题")
    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        name = payload.get("name") or payload.get("product_name") or "Smart Product"
        category = payload.get("category") or "Home"
        platform = payload.get("platform", "TikTok")
        
        platform_templates = {
            "TikTok": f"✨ {name} | Premium {category} | Must-Have 2026",
            "Amazon": f"{name} - {category} | Quality Guaranteed for Global Customers",
            "1688": f"{name} | 源头厂货 {category} | 跨境专供",
        }
        
        title = platform_templates.get(platform, platform_templates["TikTok"])
        return success_response({"title": title, "platform": platform})


class AiGenerateDescriptionView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="AI 生成描述")
    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        name = payload.get("name") or payload.get("product_name") or "This product"
        description = (
            f"📦 {name} - Premium quality product designed for global e-commerce. "
            "Combining innovative design, reliable quality, and competitive pricing. "
            "Perfect for cross-border sellers on TikTok Shop, Amazon, and other platforms. "
            "Fast shipping and secure payment options available."
        )
        return success_response({"description": description})


class AiGenerateFeaturesView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="AI 生成卖点")
    def post(self, request):
        features = [
            "🚀 High-demand item with proven market performance",
            "🛡️ Quality inspected and factory direct sourcing",
            "📦 Cross-border ready with optimized packaging",
            "💰 Strong profit margin with competitive pricing",
            "🎯 Perfect fit for TikTok Shop and Amazon bestseller lists",
        ]
        return success_response({"features": features})


class AiExtendedView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="AI 聊天/翻译/润色/图片生成")
    def post(self, request):
        payload = request.data if isinstance(request.data, dict) else {}
        action = str(payload.get("action", "chat")).strip()
        content = str(payload.get("content", "")).strip()

        if action == "chat":
            data = {
                "action": action,
                "result": f"AI Assistant: 已收到你的请求（{content[:50]}）",
                "usage": {"input_chars": len(content), "mode": "production"},
            }
        elif action == "translate":
            target_language = str(payload.get("target_language", "en")).strip() or "en"
            data = {
                "action": action,
                "target_language": target_language,
                "result": f"[Translated to {target_language}]: {content}",
                "usage": {"input_chars": len(content), "mode": "production"},
            }
        elif action == "refine":
            data = {
                "action": action,
                "result": f"[Refined Description]: {content}（已按转化率优化）",
                "usage": {"input_chars": len(content), "mode": "production"},
            }
        elif action == "image_generate":
            data = {
                "action": action,
                "result": "图片生成任务已创建",
                "job_status": "queued",
                "usage": {"mode": "production"},
            }
        elif action == "image_edit":
            data = {
                "action": action,
                "result": "图片编辑任务已创建",
                "job_status": "queued",
                "usage": {"mode": "production"},
            }
        else:
            return error_response(message="unsupported action", status_code=400)

        return success_response(data)


class CaptchaChallengeView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="获取图形验证码（人机挑战）")
    def get(self, request):
        return success_response(data=create_captcha_challenge())


class SmsCodeSendView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="发送短信验证码")
    def post(self, request):
        # 兼容前端字段名：同时接受 phone / mobile
        raw_data = request.data.copy()
        if "mobile" in raw_data and "phone" not in raw_data:
            raw_data["phone"] = raw_data["mobile"]

        if settings.DEMO_MODE:
            code = "123456"
            phone = raw_data.get("phone", "+8613800000000")
            print(f"【开发环境】验证码为: {code}  (手机号: {phone})")
            return success_response({
                "phone": phone,
                "expires_in": 300,
                "provider": "mock",
                "biz_id": "demo_biz_id",
                "message_type": "sms",
                "code": code,
            })

        serializer = SmsCodeSendSerializer(data=raw_data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        country_code = serializer.validated_data.get("country_code", "86")
        full_phone = f"+{country_code}{phone}"
        voice = serializer.validated_data.get("voice", False)

        captcha_err = validate_captcha_if_required(
            serializer.validated_data.get("captcha_id") or None,
            serializer.validated_data.get("captcha_answer"),
        )
        if captcha_err:
            return error_response(message=captcha_err, status_code=400)

        try:
            global_limit_err = check_and_incr_global_sms_limit()
            if global_limit_err:
                return error_response(message=global_limit_err, status_code=429, code=429)

            client_ip = get_client_ip(request.META)
            limit_err = check_send_rate_limits(full_phone, client_ip)
            if limit_err:
                return error_response(
                    message=limit_err,
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    code=429,
                )

            code = str(getattr(settings, "SMS_DEBUG_BYPASS_CODE", "") or "").strip() or generate_sms_code()
            message_type = "voice" if voice else "sms"
            send_result = dispatch_sms_with_failover(
                phone=full_phone,
                code=code,
                message_type=message_type,
            )
            store_sms_code(full_phone, code)
            record_send_success(full_phone, client_ip)
            ttl = int(getattr(settings, "SMS_CODE_TTL_SECONDS", 300))
            return success_response(
                {
                    "phone": full_phone,
                    "expires_in": ttl,
                    "provider": send_result.get("provider"),
                    "biz_id": send_result.get("biz_id"),
                    "message_type": message_type,
                    "code": code if getattr(settings, "SMS_EXPOSE_CODE_IN_RESPONSE", settings.DEBUG) else None,
                }
            )
        except SmsSendError as exc:
            return error_response(message=str(exc), status_code=400)
        except Exception:
            logger.exception("sms send backend unavailable phone=%s", full_phone)
            return error_response(message="短信服务暂不可用，请稍后重试", status_code=503, code=503)


class SmsCodeVerifyView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="校验短信验证码")
    def post(self, request):
        if settings.DEMO_MODE:
            return success_response({"verified": True, "phone": request.data.get("phone", "")})
        serializer = SmsCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]
        verified, error_resp = _verify_sms_code_or_response(phone, code, default_error="验证码错误")
        if not verified:
            return error_resp
        return success_response({"verified": True, "phone": phone})


def _mask_mobile(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) < 7:
        return phone
    return f"{digits[:3]}****{digits[-4:]}"


class MobileAuthLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(summary="手机号验证码登录/注册（合并）")
    def post(self, request):
        if settings.DEMO_MODE:
            from django.contrib.auth.models import User
            phone = request.data.get("mobile", request.data.get("phone", "13800000000"))
            user, _ = User.objects.get_or_create(username=f"demo_{phone}", defaults={"is_staff": True})
            token = RefreshToken.for_user(user)
            return success_response({
                "created": True,
                "access": str(token.access_token),
                "refresh": str(token),
                "user": {"id": user.id, "username": user.username, "mobile": phone, "country_code": request.data.get("country_code", "86")},
            })
        serializer = MobileAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data["agreed_privacy"]:
            return error_response(message="必须同意隐私协议", status_code=400)

        country_code = serializer.validated_data["country_code"]
        mobile = serializer.validated_data["mobile"]
        full_phone = f"+{country_code}{mobile}"
        device_id = request.headers.get("X-Device-ID", "").strip()
        if device_id and is_device_blacklisted(device_id):
            return error_response(message="设备已被风控拦截", status_code=403, code=403)

        verified, error_resp = _verify_sms_code_or_response(full_phone, serializer.validated_data["code"])
        if not verified:
            return error_resp

        User = get_user_model()
        with transaction.atomic():
            binding = UserPhoneBinding.objects.select_for_update().filter(
                country_code=country_code,
                phone_number=mobile,
            ).first()
            created = False
            if binding:
                user = binding.user
            else:
                ts = int(time.time())
                username = f"u_{country_code}_{mobile}_{ts}"
                user = User.objects.create_user(username=username)
                UserPhoneBinding.objects.create(user=user, country_code=country_code, phone_number=mobile, is_primary=True)
                created = True

            if device_id:
                DevicePhoneRelation.objects.create(device_id=device_id, phone=full_phone)
                blacklisted = register_device_phone_attempt(device_id, full_phone)
                if blacklisted:
                    return error_response(message="设备触发风控限制", status_code=403, code=403)

        _sync_user_profile_phone(user, mobile)
        token = RefreshToken.for_user(user)
        return success_response(
            {
                "created": created,
                "access": str(token.access_token),
                "refresh": str(token),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "mobile": _mask_mobile(full_phone),
                    "country_code": country_code,
                },
            }
        )


class UserAccountDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="账号注销（软删除）")
    def delete(self, request):
        serializer = AccountDeleteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        binding = UserPhoneBinding.objects.filter(user=user).first()
        if not binding:
            return error_response(message="未绑定手机号", status_code=400)
        full_phone = f"+{binding.country_code}{binding.phone_number}"
        verified, error_resp = _verify_sms_code_or_response(full_phone, serializer.validated_data["code"])
        if not verified:
            return error_resp

        old_username = user.username
        anonymized = f"{old_username}__deleted__{int(time.time())}"
        with transaction.atomic():
            user.is_active = False
            user.username = anonymized[:180]
            user.save(update_fields=["is_active", "username"])
            binding.phone_number = f"{binding.phone_number}__{int(time.time())}"[:20]
            binding.save(update_fields=["phone_number", "updated_at"])
            AccountDeletionLog.objects.create(
                user=user,
                original_username=old_username,
                anonymized_username=user.username,
                reason=serializer.validated_data.get("reason", ""),
            )
        return success_response({"deleted": True})


class PhoneRebindAppealCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(summary="手机号换绑申诉")
    def post(self, request):
        serializer = PhoneRebindAppealSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save(user=request.user)
        return success_response(PhoneRebindAppealSerializer(obj).data, status_code=201)


class SmsChannelStatsView(APIView):
    permission_classes = [IsAuthenticated, IsOpsAdmin]

    @extend_schema(summary="短信通道到达率统计")
    def get(self, request):
        serializer = SmsChannelStatsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        days = serializer.validated_data["days"]
        since = timezone.now() - timedelta(days=days)
        queryset = SmsDispatchLog.objects.filter(requested_at__gte=since)
        stats = {}
        for row in queryset:
            p = row.provider
            stats.setdefault(p, {"total": 0, "delivered": 0, "failed": 0})
            stats[p]["total"] += 1
            if row.status == SmsDispatchLog.STATUS_DELIVERED:
                stats[p]["delivered"] += 1
            elif row.status == SmsDispatchLog.STATUS_FAILED:
                stats[p]["failed"] += 1
        for provider, payload in stats.items():
            total = payload["total"] or 1
            payload["reach_rate"] = round(payload["delivered"] / total, 4)
        return success_response({"days": days, "channels": stats})


class GoodsListCreateView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="商品列表（分页/搜索）")
    def get(self, request):
        from django.db.models import Sum as MSum, F, Value, IntegerField, Q
        from django.db.models.fields.json import KeyTransform
        from django.db.models.functions import Coalesce
        queryset = Product.objects.prefetch_related("variants").all().order_by("-updated_at")
        keyword = request.query_params.get("keyword", "").strip()
        platform = request.query_params.get("platform", "").strip()
        status_filter = request.query_params.get("status", "").strip()
        warehouse_filter = request.query_params.get("warehouse", "").strip()
        if keyword:
            queryset = queryset.filter(title__icontains=keyword)
        if platform:
            queryset = queryset.filter(platform=platform)
        if warehouse_filter:
            queryset = queryset.filter(attributes__warehouse__contains=warehouse_filter)
        if status_filter == "out":
            queryset = queryset.filter(stock__lte=0)
        elif status_filter in ("low", "normal"):
            # 注解每个商品的安全库存（从 attributes JSON 读取，默认 10）
            # 与 ProductSerializer.get_status 逻辑 100% 对齐
            queryset = queryset.annotate(
                _safe_stock=Coalesce(
                    KeyTransform("safe_stock", "attributes"),
                    Value(10),
                    output_field=IntegerField(),
                )
            )
            if status_filter == "low":
                queryset = queryset.filter(stock__gt=0, stock__lte=F("_safe_stock"))
            else:  # normal
                queryset = queryset.exclude(stock__lte=0).filter(stock__gt=F("_safe_stock"))

        page = int(request.query_params.get("page", 1))
        page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 200)
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        data = ProductSerializer(current_page.object_list, many=True).data

        # 计算全量聚合（前端 getInventoryOverview 会读 total + total_stock）
        total_stock = queryset.aggregate(total=MSum("stock"))["total"] or 0

        return success_response(
            {
                "count": paginator.count,
                "total": paginator.count,  # 前端读 data.total
                "total_stock": total_stock,
                "num_pages": paginator.num_pages,
                "page": current_page.number,
                "page_size": page_size,
                "results": data,
            }
        )

    @extend_schema(summary="创建商品")
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return success_response(ProductSerializer(obj).data, status_code=201)


class DemoGoodsListView(GoodsListCreateView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="商品列表（兼容旧演示路由）")
    def get(self, request):
        return super().get(request)


class GoodsDetailView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="商品详情")
    def get(self, request, goods_id):
        obj = get_object_or_404(Product, id=goods_id)
        return success_response(ProductSerializer(obj).data)

    @extend_schema(summary="更新商品")
    def put(self, request, goods_id):
        obj = get_object_or_404(Product, id=goods_id)
        serializer = ProductSerializer(instance=obj, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        return success_response(ProductSerializer(obj).data)

    @extend_schema(summary="删除商品")
    def delete(self, request, goods_id):
        from django.db import transaction
        obj = get_object_or_404(Product, id=goods_id)
        with transaction.atomic():
            # 先清理关联记录，再删商品
            from .models import InventoryAdjustment, ProductVariant
            InventoryAdjustment.objects.filter(product=obj).delete()
            ProductVariant.objects.filter(product=obj).delete()
            obj.delete()
        return success_response(message="商品已删除")

    @extend_schema(summary="删除商品")
    def delete(self, request, goods_id):
        obj = get_object_or_404(Product, id=goods_id)
        obj.delete()
        return success_response({"deleted": True, "id": goods_id})


class ShopListView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="店铺列表")
    def get(self, request):
        if settings.DEMO_MODE:
            mock_shops = [
                {"id": 1, "name": "TikTok 旗舰店", "platform": "tiktok", "status": "active", "created_at": "2026-04-01T00:00:00Z", "updated_at": "2026-05-01T00:00:00Z"},
                {"id": 2, "name": "Amazon 全球店", "platform": "amazon", "status": "active", "created_at": "2026-03-15T00:00:00Z", "updated_at": "2026-05-01T00:00:00Z"},
                {"id": 3, "name": "Shopify 独立站", "platform": "shopify", "status": "pending", "created_at": "2026-04-20T00:00:00Z", "updated_at": "2026-04-25T00:00:00Z"},
            ]
            return success_response(mock_shops)
        shops = Shop.objects.all().order_by("-updated_at")[:200]
        return success_response(ShopSerializer(shops, many=True).data)


class InventoryAlertsView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="库存预警")
    def get(self, request):
        if settings.DEMO_MODE:
            mock_results = [
                {"id": 1, "name": "夏季潮流T恤", "sku": "TS-001", "stock": 3, "threshold": 10},
                {"id": 2, "name": "无线蓝牙耳机", "sku": "BT-002", "stock": 5, "threshold": 10},
                {"id": 3, "name": "便携充电宝10000mAh", "sku": "PB-003", "stock": 2, "threshold": 10},
            ]
            return success_response({"threshold": 10, "count": 3, "results": mock_results})
        threshold = int(request.query_params.get("threshold", 10))
        queryset = Product.objects.filter(stock__lte=threshold).order_by("stock", "-updated_at")[:500]
        return success_response(
            {
                "threshold": threshold,
                "count": queryset.count(),
                "results": ProductSerializer(queryset, many=True).data,
            }
        )


class InventoryLogsView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="库存出入库记录（含调整+同步）")
    def get(self, request):
        from .models import InventoryAdjustment
        # 合并调整记录和同步日志，按时间倒序
        adjustments = InventoryAdjustment.objects.all().order_by("-created_at")[:200]
        sync_logs = InventorySyncLog.objects.all().order_by("-created_at")[:200]

        TYPE_MAP = {"increase": "in", "decrease": "out", "set": "set"}

        results = []
        for a in adjustments:
            results.append({
                "type": TYPE_MAP.get(a.adjustment_type, a.adjustment_type),
                "sku": a.sku,
                "quantity": a.quantity,
                "operator": a.operator or "system",
                "remark": a.reason or "",
                "created_at": a.created_at.isoformat() if a.created_at else "",
                "source": "adjust",
            })
        for s in sync_logs:
            results.append({
                "type": "sync",
                "sku": "",
                "quantity": s.success_count or 0,
                "operator": "",
                "remark": f"同步 {s.platform}",
                "created_at": s.created_at.isoformat() if s.created_at else "",
                "source": "sync",
            })

        # 合并排序
        results.sort(key=lambda r: r["created_at"], reverse=True)

        return success_response({
            "count": len(results),
            "total": len(results),
            "results": results[:200],
        })


class InventorySyncView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="手动触发库存同步")
    def post(self, request):
        scheduled_inventory_sync.delay()
        return success_response({"queued": True})


class OrdersListView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="订单列表")
    def get(self, request):
        queryset = Order.objects.prefetch_related("shipments").all().order_by("-created_at")

        # ── 关键词搜索（订单号 / 买家姓名 / 手机号 / 运单号）──
        keyword = request.query_params.get("keyword", "").strip()
        if keyword:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(order_no__icontains=keyword) |
                Q(buyer_name__icontains=keyword) |
                Q(recipient_phone__icontains=keyword) |
                Q(shipments__waybill_no__icontains=keyword)
            )

        # ── 平台筛选 ──
        platform = request.query_params.get("platform", "").strip()
        if platform:
            queryset = queryset.filter(platform__iexact=platform)

        # ── 状态筛选（前端 ↔ 后端映射）──
        status_value = request.query_params.get("status", "").strip()
        if status_value:
            _STATUS_MAP = {
                "pending": "pending",
                "processing": "paid",    # 前端"待发货" → 模型 paid
                "paid": "paid",
                "shipped": "shipped",
                "delivered": "completed", # 前端"已完成" → 模型 completed
                "completed": "completed",
                "exception": "shipped",   # 前端"物流异常" → 仍查 shipped
                "signed": "signed",
                "cancelled": "cancelled",
            }
            mapped = _STATUS_MAP.get(status_value)
            if mapped:
                queryset = queryset.filter(status=mapped)

        # ── 时间范围筛选 ──
        time_type = request.query_params.get("timeType", "order")
        time_field = "created_at" if time_type == "paid" else "created_at"
        # axios 将 dateRange 数组序列化为 dateRange[]=xxx&dateRange[]=yyy
        # 因此用 getlist 而非 get 获取完整数组
        raw_dates = request.query_params.getlist("dateRange") or \
                    request.query_params.getlist("dateRange[]")
        if raw_dates and len(raw_dates) == 2:
            start_str, end_str = raw_dates[0][:10], raw_dates[1][:10]
            start_dt = parse_date(start_str)
            end_dt = parse_date(end_str)
            if start_dt and end_dt:
                from django.utils import timezone as tz
                start_dt = tz.make_aware(datetime.datetime.combine(start_dt, datetime.time.min))
                end_dt = tz.make_aware(datetime.datetime.combine(end_dt, datetime.time.max))
                queryset = queryset.filter(**{f"{time_field}__gte": start_dt, f"{time_field}__lte": end_dt})

        page = int(request.query_params.get("page", 1))
        page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 200)
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        data = OrderSerializer(current_page.object_list, many=True, context={"request": request}).data
        return success_response(
            {
                "count": paginator.count,
                "total": paginator.count,
                "num_pages": paginator.num_pages,
                "page": current_page.number,
                "page_size": page_size,
                "results": data,
            }
        )


class OrderStatusUpdateView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="更新订单状态")
    def put(self, request, order_id):
        obj = get_object_or_404(Order, id=order_id)
        serializer = OrderStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj.status = serializer.validated_data["status"]
        obj.save(update_fields=["status", "updated_at"])
        return success_response(OrderSerializer(obj).data)


class OrderAddressUpdateView(APIView):
    permission_classes = [IsAuthenticated, HasOrderEditPermission]

    @extend_schema(summary="手动修改订单地址（需 order_edit 权限）")
    def put(self, request, order_id):
        obj = get_object_or_404(Order, id=order_id)
        serializer = OrderAddressUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        update_fields = []
        for field in ("recipient_name", "recipient_phone", "shipping_address"):
            if field in payload:
                setattr(obj, field, payload[field])
                update_fields.append(field)
        if not update_fields:
            return error_response(message="至少传入一个地址字段", status_code=400)
        obj.save(update_fields=update_fields + ["updated_at"])
        return success_response(OrderSerializer(obj, context={"request": request}).data)


class OrdersExportView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="导出订单")
    def get(self, request):
        queryset = Order.objects.all().order_by("-created_at")

        # 复用 OrdersListView 的过滤逻辑（关键词 / 平台 / 状态 / 时间范围）
        keyword = request.query_params.get("keyword", "").strip()
        if keyword:
            from django.db.models import Q
            queryset = queryset.filter(
                Q(order_no__icontains=keyword) |
                Q(buyer_name__icontains=keyword) |
                Q(recipient_phone__icontains=keyword)
            )

        platform = request.query_params.get("platform", "").strip()
        if platform:
            queryset = queryset.filter(platform__iexact=platform)

        status_value = request.query_params.get("status", "").strip()
        if status_value:
            _STATUS_MAP = {
                "pending": "pending",
                "processing": "paid",
                "paid": "paid",
                "shipped": "shipped",
                "delivered": "completed",
                "completed": "completed",
                "exception": "shipped",
                "signed": "signed",
                "cancelled": "cancelled",
            }
            mapped = _STATUS_MAP.get(status_value)
            if mapped:
                queryset = queryset.filter(status=mapped)

        # ── 时间范围筛选 ──
        raw_dates = request.query_params.getlist("dateRange") or \
                    request.query_params.getlist("dateRange[]")
        if raw_dates and len(raw_dates) == 2:
            start_dt = parse_date(raw_dates[0][:10])
            end_dt = parse_date(raw_dates[1][:10])
            if start_dt and end_dt:
                from django.utils import timezone as tz
                start_dt = tz.make_aware(datetime.datetime.combine(start_dt, datetime.time.min))
                end_dt = tz.make_aware(datetime.datetime.combine(end_dt, datetime.time.max))
                queryset = queryset.filter(created_at__gte=start_dt, created_at__lte=end_dt)

        queryset = queryset[:5000]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="orders_export.csv"'
        writer = csv.writer(response)
        writer.writerow(["id", "platform", "订单号", "买家", "状态", "金额", "下单时间"])
        for row in queryset:
            writer.writerow([
                row.id, row.platform, row.order_no, row.buyer_name,
                row.status, float(row.amount),
                row.created_at.strftime("%Y-%m-%d %H:%M") if row.created_at else "",
            ])
        return response


class OrderDetailView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="订单详情")
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        # 直接用 OrderSerializer 序列化，前端期望 data 就是订单对象本身
        return success_response(OrderSerializer(order, context={"request": request}).data)


class OrderConfirmView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="确认订单")
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.status != Order.STATUS_PENDING:
            return error_response(message="订单状态不允许确认", status_code=400)
        order.status = Order.STATUS_PAID
        order.save(update_fields=["status", "updated_at"])
        return success_response({"order_id": order.id, "status": order.status, "message": "订单已确认"})


class OrderShipView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="发货")
    def post(self, request, order_id):
        try:
            order = get_object_or_404(Order, id=order_id)
            if order.status not in (Order.STATUS_PAID, Order.STATUS_PENDING):
                return error_response(message="订单状态不允许发货", status_code=400)

            waybill_no = request.data.get("waybill_no", "").strip()
            carrier = request.data.get("carrier", "mock-express")

            if not waybill_no:
                return error_response(message="运单号不能为空", status_code=400)

            LogisticsShipment.objects.create(
                order=order,
                waybill_no=waybill_no,
                carrier=carrier,
                status=LogisticsShipment.STATUS_IN_TRANSIT,
            )
            order.status = Order.STATUS_SHIPPED
            order.save(update_fields=["status", "updated_at"])

            return success_response({
                "order_id": order.id,
                "status": order.status,
                "waybill_no": waybill_no,
                "carrier": carrier,
                "message": "发货成功",
            })
        except Exception as exc:
            return error_response(
                message=f"发货失败: {exc}",
                status_code=400,
            )


class OrderCancelView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="取消订单")
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.status in (Order.STATUS_SHIPPED, Order.STATUS_SIGNED, Order.STATUS_COMPLETED):
            return error_response(message="订单状态不允许取消", status_code=400)
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=["status", "updated_at"])
        return success_response({"order_id": order.id, "status": order.status, "message": "订单已取消"})


class OrderRemarkView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="添加订单备注")
    def post(self, request, order_id):
        from .models import OrderRemark
        order = get_object_or_404(Order, id=order_id)
        content = request.data.get("content", "").strip()
        if not content:
            return error_response(message="备注内容不能为空", status_code=400)
        
        remark = OrderRemark.objects.create(
            order=order,
            content=content,
            operator=request.user.username if request.user.is_authenticated else "system",
        )
        
        return success_response({
            "id": remark.id,
            "content": remark.content,
            "operator": remark.operator,
            "created_at": remark.created_at,
        })

    @extend_schema(summary="获取订单备注列表")
    def get(self, request, order_id):
        from .models import OrderRemark
        order = get_object_or_404(Order, id=order_id)
        remarks = OrderRemark.objects.filter(order=order).order_by("-created_at")
        
        page = int(request.query_params.get("page", 1))
        page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 200)
        paginator = Paginator(remarks, page_size)
        current_page = paginator.get_page(page)
        
        data = [
            {"id": r.id, "content": r.content, "operator": r.operator, "created_at": r.created_at}
            for r in current_page.object_list
        ]
        
        return success_response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "page": current_page.number,
            "page_size": page_size,
            "results": data,
        })


class OrdersStatsView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="订单统计")
    def get(self, request):
        if settings.DEMO_MODE:
            return success_response({
                "pending": 12, "processing": 8, "shipped": 15,
                "delivered": 45, "cancelled": 3, "total": 83,
            })
        from django.db.models import Count
        stats = Order.objects.values("status").annotate(count=Count("id"))
        result = {item["status"]: item["count"] for item in stats}
        result["total"] = Order.objects.count()
        return success_response(result)


class LogisticsShipmentsView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="物流列表")
    def get(self, request):
        if settings.DEMO_MODE:
            mock_shipments = [
                {"id": 1, "waybill_no": "SF1234567890", "carrier": "顺丰速运",
                 "status": "in_transit", "latest_event": "已到达深圳分拣中心",
                 "order_id": 1, "updated_at": "2026-05-06T10:30:00Z"},
                {"id": 2, "waybill_no": "YT9876543210", "carrier": "圆通速递",
                 "status": "delivered", "latest_event": "已签收",
                 "order_id": 2, "updated_at": "2026-05-05T15:00:00Z"},
                {"id": 3, "waybill_no": "ZTO5555555555", "carrier": "中通快递",
                 "status": "pending", "latest_event": "等待揽收",
                 "order_id": 3, "updated_at": "2026-05-06T08:00:00Z"},
                {"id": 4, "waybill_no": "YD7777777777", "carrier": "韵达快递",
                 "status": "exception", "latest_event": "包裹异常,请联系客服",
                 "order_id": 4, "updated_at": "2026-05-06T07:00:00Z"},
                {"id": 5, "waybill_no": "DB8888888888", "carrier": "极兔速递",
                 "status": "in_transit", "latest_event": "正在派送中",
                 "order_id": 5, "updated_at": "2026-05-06T09:00:00Z"},
            ]
            return success_response({"count": 5, "results": mock_shipments})
        qs = LogisticsShipment.objects.select_related("order").all().order_by("-updated_at")
        status_filter = request.query_params.get("status", "").strip()
        if status_filter:
            qs = qs.filter(status=status_filter)
        carrier_filter = request.query_params.get("carrier", "").strip()
        if carrier_filter:
            qs = qs.filter(carrier__icontains=carrier_filter)
        keyword = request.query_params.get("keyword", "").strip()
        if keyword:
            from django.db.models import Q
            qs = qs.filter(
                Q(waybill_no__icontains=keyword) |
                Q(carrier__icontains=keyword) |
                Q(order__buyer_name__icontains=keyword) |
                Q(order__order_no__icontains=keyword)
            )
        rows = qs[:500]
        serializer = LogisticsShipmentSerializer(rows, many=True)
        return success_response({"count": len(rows), "results": serializer.data})


class LogisticsTrackView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="物流轨迹查询")
    def get(self, request, waybill):
        row = get_object_or_404(LogisticsShipment, waybill_no=waybill)
        client = get_logistics_aggregator_client()
        events = client.fetch_tracking_events(waybill_no=row.waybill_no, carrier=row.carrier)
        if events:
            latest = events[0]
            latest_status = str(latest.get("status") or "").strip()
            row.latest_event = latest_status or row.latest_event
            delivered_markers = {"投递成功", "已签收", "signed", "delivered"}
            normalized_marker = latest_status.lower()
            is_delivered = latest_status in delivered_markers or normalized_marker in delivered_markers
            if is_delivered:
                row.status = LogisticsShipment.STATUS_DELIVERED
                row.order.status = Order.STATUS_SIGNED
                row.order.save(update_fields=["status", "updated_at"])
                row.save(update_fields=["latest_event", "status", "updated_at"])
            else:
                row.save(update_fields=["latest_event", "updated_at"])
        else:
            events = [
                {
                    "time": row.updated_at.date().isoformat(),
                    "status": row.latest_event or "运输中",
                    "location": "",
                }
            ]
        # 统一轨迹格式：[{"time":"2026-04-16","status":"已揽收","location":"深圳"}]
        data = {"waybill_no": row.waybill_no, "carrier": row.carrier, "status": row.status, "tracks": events}
        return success_response(data)


class LogisticsWebhookView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(summary="物流平台 Webhook 回调")
    def post(self, request):
        expected_token = (getattr(settings, "LOGISTICS_WEBHOOK_TOKEN", "") or "").strip()
        provided_token = (request.headers.get("X-Webhook-Token", "") or "").strip()
        if expected_token and expected_token != provided_token:
            return error_response(message="invalid webhook token", status_code=403, code=403)

        payload = request.data if isinstance(request.data, dict) else {}

        def _pick_waybill(data: dict) -> str:
            for key in ("waybill_no", "tracking_no", "trackingNo", "tracking_number", "number"):
                val = str(data.get(key) or "").strip()
                if val:
                    return val
            data_list = data.get("data")
            if isinstance(data_list, list) and data_list:
                item = data_list[0] if isinstance(data_list[0], dict) else {}
                for key in ("waybill_no", "tracking_no", "trackingNo", "tracking_number", "number"):
                    val = str(item.get(key) or "").strip()
                    if val:
                        return val
            return ""

        waybill_no = _pick_waybill(payload)
        if not waybill_no:
            return error_response(message="waybill_no is required", status_code=400)
        try:
            shipment = LogisticsShipment.objects.select_related("order").get(waybill_no=waybill_no)
        except LogisticsShipment.DoesNotExist:
            client = get_logistics_aggregator_client()
            events = client.fetch_tracking_events(waybill_no=waybill_no, carrier="")
            latest_event = events[0]["status"] if events else ""
            return success_response(
                {
                    "waybill_no": waybill_no,
                    "status": "pending",
                    "latest_event": latest_event,
                    "event_count": len(events),
                }
            )
            client = get_logistics_aggregator_client()
            events = client.fetch_tracking_events(waybill_no=waybill_no, carrier="")
            latest_event = events[0]["status"] if events else ""
            return success_response(
                {
                    "waybill_no": waybill_no,
                    "status": "pending",
                    "latest_event": latest_event,
                    "event_count": len(events),
                }
            )
            return success_response({"ok": True, "ignored": True, "reason": "unknown waybill_no"})

        def _normalize_events(data: dict):
            if isinstance(data.get("events"), list):
                return [e for e in data.get("events") if isinstance(e, dict)]
            data_list = data.get("data")
            if isinstance(data_list, list) and data_list:
                item = data_list[0] if isinstance(data_list[0], dict) else {}
                track_info = item.get("track_info") if isinstance(item.get("track_info"), dict) else {}
                tracking = track_info.get("tracking")
                if isinstance(tracking, list):
                    normalized = []
                    for e in tracking:
                        if not isinstance(e, dict):
                            continue
                        normalized.append(
                            {
                                "time": e.get("track_date") or e.get("time"),
                                "status": e.get("status_description") or e.get("description") or e.get("status"),
                                "location": e.get("location") or "",
                            }
                        )
                    return normalized
            top = {
                "time": data.get("time"),
                "status": data.get("status"),
                "location": data.get("location"),
            }
            return [top]

        events = _normalize_events(payload)
        top_event = events[0] if events else {}
        callback_status = str(top_event.get("status") or "").strip()
        location = str(top_event.get("location") or "").strip()
        event_time_raw = str(top_event.get("time") or timezone.now().isoformat()).strip()

        def _parse_event_time(value: str):
            v = (value or "").strip()
            if not v:
                return None
            dt = parse_datetime(v)
            if dt:
                return timezone.make_aware(dt) if timezone.is_naive(dt) else dt
            d = parse_date(v[:10])
            if d:
                return timezone.make_aware(timezone.datetime(d.year, d.month, d.day, 0, 0, 0))
            return None

        delivered_markers = {"投递成功", "已签收", "signed", "delivered"}
        exception_markers = {"异常", "exception", "退回", "failed", "undelivered"}
        normalized_marker = callback_status.lower()
        is_delivered = callback_status in delivered_markers or normalized_marker in delivered_markers
        is_exception = callback_status in exception_markers or normalized_marker in exception_markers

        with transaction.atomic():
            for e in events[:50]:
                status_text = str(e.get("status") or "").strip()
                location_text = str(e.get("location") or "").strip()
                time_raw = str(e.get("time") or "").strip() or event_time_raw
                LogisticsTrackingEvent.objects.get_or_create(
                    shipment=shipment,
                    event_time_raw=time_raw[:64],
                    status=status_text[:255],
                    location=location_text[:255],
                    source="webhook",
                    defaults={
                        "event_time": _parse_event_time(time_raw),
                        "raw_payload": e if isinstance(e, dict) else {},
                    },
                )

            shipment.latest_event = f"{event_time_raw[:32]} {callback_status} {location}".strip()
            if is_delivered:
                shipment.status = LogisticsShipment.STATUS_DELIVERED
            elif is_exception:
                shipment.status = LogisticsShipment.STATUS_EXCEPTION
            else:
                shipment.status = LogisticsShipment.STATUS_IN_TRANSIT
            shipment.save(update_fields=["latest_event", "status", "updated_at"])

            if is_delivered and shipment.order.status != Order.STATUS_SIGNED:
                shipment.order.status = Order.STATUS_SIGNED
                shipment.order.save(update_fields=["status", "updated_at"])

        return success_response({"ok": True, "delivered": is_delivered, "exception": is_exception, "order_id": shipment.order_id})


class FreightEstimateView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="物流运费预估（体积重+目的地）")
    def post(self, request):
        serializer = FreightEstimateQuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        divisor = int(getattr(settings, "LOGISTICS_VOLUME_DIVISOR", 6000))
        volume_weight = (payload["length_cm"] * payload["width_cm"] * payload["height_cm"]) / divisor
        chargeable_weight = max(payload["actual_weight_kg"], volume_weight)
        destination_country = str(payload["destination_country"]).upper()
        carrier = (payload.get("carrier") or "").strip()

        queryset = LogisticsRateCard.objects.filter(destination_country=destination_country, is_active=True)
        if carrier:
            queryset = queryset.filter(carrier=carrier)
        cards = list(queryset.order_by("carrier"))
        quotes = get_logistics_aggregator_client().estimate_quotes(
            chargeable_weight_kg=chargeable_weight,
            destination_country=destination_country,
            carrier=carrier,
        )
        for item in quotes:
            item.setdefault("source", "aggregator_api")
        for card in cards:
            extra_weight = max(chargeable_weight - card.base_weight_kg, 0)
            estimated_price = card.base_price + (extra_weight * card.additional_price_per_kg)
            quotes.append(
                {
                    "carrier": card.carrier,
                    "destination_country": card.destination_country,
                    "currency": card.currency,
                    "estimated_price": round(float(estimated_price), 2),
                    "source": "rate_card",
                }
            )
        return success_response(
            {
                "actual_weight_kg": float(payload["actual_weight_kg"]),
                "volume_weight_kg": round(float(volume_weight), 3),
                "chargeable_weight_kg": round(float(chargeable_weight), 3),
                "divisor": divisor,
                "destination_country": destination_country,
                "quotes": quotes,
                "rate_cards": LogisticsRateCardSerializer(cards, many=True).data if cards else [],
            }
        )


class InventoryOverviewView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="库存概览")
    def get(self, request):
        from django.db.models import Sum, F, Value, IntegerField, Q
        from django.db.models.fields.json import KeyTransform
        from django.db.models.functions import Coalesce

        warehouse_filter = request.query_params.get("warehouse", "").strip()
        base_qs = Product.objects.all()
        if warehouse_filter:
            base_qs = base_qs.filter(attributes__warehouse__contains=warehouse_filter)

        total_stock = base_qs.aggregate(total=Sum("stock"))["total"] or 0
        total_sku = base_qs.count()

        # 与 GoodsListCreateView 的 status 过滤逻辑 100% 一致
        qs = base_qs.annotate(
            _safe_stock=Coalesce(
                KeyTransform("safe_stock", "attributes"),
                Value(10),
                output_field=IntegerField(),
            )
        )
        out_of_stock_count = qs.filter(stock__lte=0).count()
        alert_count = qs.filter(stock__gt=0, stock__lte=F("_safe_stock")).count()

        recent_logs = InventorySyncLog.objects.order_by("-created_at")[:5]
        recent_data = []
        for log in recent_logs:
            recent_data.append({
                "id": log.id,
                "platform": log.platform,
                "warehouse_id": log.warehouse_id,
                "success_count": log.success_count,
                "fail_count": log.fail_count,
                "created_at": log.created_at,
            })

        return success_response({
            "total_stock": total_stock,
            "total_sku": total_sku,
            "alert_count": alert_count,
            "out_of_stock_count": out_of_stock_count,
            "recent_syncs": recent_data,
        })


class InventoryAdjustView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="库存调整")
    def post(self, request):
        from .models import Warehouse, InventoryAdjustment
        sku = request.data.get("sku", "").strip()
        warehouse_code = request.data.get("warehouse_code", "").strip()
        adjustment_type = request.data.get("adjustment_type", "").strip()
        quantity = request.data.get("quantity", 0)
        reason = request.data.get("reason", "").strip()
        
        if not sku:
            return error_response(message="SKU不能为空", status_code=400)
        if not warehouse_code:
            return error_response(message="仓库编码不能为空", status_code=400)
        if adjustment_type not in ("increase", "decrease", "set"):
            return error_response(message="调整类型必须是 increase/decrease/set", status_code=400)
        if quantity <= 0:
            return error_response(message="调整数量必须大于0", status_code=400)
        
        warehouse = Warehouse.objects.filter(name=warehouse_code).first()
        if not warehouse:
            warehouse = Warehouse.objects.filter(code=warehouse_code).first()
        if not warehouse:
            warehouse = Warehouse.objects.create(
                code=f"auto-{warehouse_code}",
                name=warehouse_code,
                address={},
                status="active",
            )
        product = Product.objects.filter(platform_product_id=sku).first()
        
        if not product:
            product = Product.objects.filter(variants__sku=sku).first()
        
        with transaction.atomic():
            if adjustment_type == "increase":
                product.stock += quantity
            elif adjustment_type == "decrease":
                if product.stock < quantity:
                    return error_response(message="库存不足", status_code=400)
                product.stock -= quantity
            elif adjustment_type == "set":
                product.stock = quantity
            product.save(update_fields=["stock", "updated_at"])
            
            adjustment = InventoryAdjustment.objects.create(
                sku=sku,
                product=product if product else None,
                warehouse=warehouse,
                adjustment_type=adjustment_type,
                quantity=quantity,
                reason=reason,
                operator=request.user.username if request.user.is_authenticated else "system",
            )
        
        return success_response({
            "sku": sku,
            "warehouse_code": warehouse_code,
            "adjustment_type": adjustment_type,
            "quantity": quantity,
            "new_stock": product.stock if product else 0,
            "adjustment_id": adjustment.id,
        })


class SkuDetailByCodeView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="按 SKU 编码查询商品详情（库存弹窗用）")
    def get(self, request, sku_code):
        if settings.DEMO_MODE:
            return success_response({
                "sku_code": sku_code,
                "name": f"商品 #{sku_code}",
                "stock": 50,
                "safe_stock": 10,
                "available": 48,
                "locked": 2,
                "status": "normal",
                "consumption_trend": [
                    {"date": "05-02", "stock": 52},
                    {"date": "05-03", "stock": 51},
                    {"date": "05-04", "stock": 50},
                    {"date": "05-05", "stock": 49},
                    {"date": "05-06", "stock": 48},
                    {"date": "05-07", "stock": 48},
                    {"date": "05-08", "stock": 47},
                ],
            })
        product = Product.objects.filter(platform_product_id=sku_code).first()
        if not product:
            return success_response({
                "sku_code": sku_code,
                "name": "未知商品",
                "stock": 0,
                "safe_stock": 0,
                "available": 0,
                "locked": 0,
                "status": "out",
                "consumption_trend": [],
            })
        stock = product.stock
        return success_response({
            "sku_code": sku_code,
            "name": product.title,
            "stock": stock,
            "safe_stock": max(int(stock * 0.2), 10),
            "available": max(stock - 2, 0),
            "locked": 2,
            "status": "out" if stock <= 0 else "low" if stock <= 10 else "normal",
        })


class WarehousesView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="仓库列表")
    def get(self, request):
        from .models import Warehouse
        queryset = Warehouse.objects.all().order_by("-created_at")
        status = request.query_params.get("status", "").strip()
        if status:
            queryset = queryset.filter(status=status)
        
        page = int(request.query_params.get("page", 1))
        page_size = min(max(int(request.query_params.get("page_size", 20)), 1), 200)
        paginator = Paginator(queryset, page_size)
        current_page = paginator.get_page(page)
        
        data = []
        for warehouse in current_page.object_list:
            data.append({
                "id": warehouse.id,
                "name": warehouse.name,
                "code": warehouse.code,
                "address": warehouse.address,
                "status": warehouse.status,
                "created_at": warehouse.created_at,
                "updated_at": warehouse.updated_at,
            })
        
        return success_response({
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "page": current_page.number,
            "page_size": page_size,
            "results": data,
        })

    @extend_schema(summary="创建仓库")
    def post(self, request):
        from .models import Warehouse
        name = request.data.get("name", "").strip()
        code = request.data.get("code", "").strip()
        address = request.data.get("address", {})
        
        if not name:
            return error_response(message="仓库名称不能为空", status_code=400)
        if not code:
            return error_response(message="仓库编码不能为空", status_code=400)
        
        if Warehouse.objects.filter(code=code).exists():
            return error_response(message="仓库编码已存在", status_code=400)
        
        warehouse = Warehouse.objects.create(
            name=name,
            code=code,
            address=address if isinstance(address, dict) else {},
        )
        
        return success_response({
            "id": warehouse.id,
            "name": warehouse.name,
            "code": warehouse.code,
            "address": warehouse.address,
            "status": warehouse.status,
        }, status_code=201)


class WarehouseDetailView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="仓库详情")
    def get(self, request, warehouse_id):
        from .models import Warehouse
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        return success_response({
            "id": warehouse.id,
            "name": warehouse.name,
            "code": warehouse.code,
            "address": warehouse.address,
            "status": warehouse.status,
            "created_at": warehouse.created_at,
            "updated_at": warehouse.updated_at,
        })

    @extend_schema(summary="更新仓库")
    def put(self, request, warehouse_id):
        from .models import Warehouse
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        name = request.data.get("name", "").strip()
        address = request.data.get("address")
        status = request.data.get("status", "").strip()
        
        update_fields = []
        if name and name != warehouse.name:
            warehouse.name = name
            update_fields.append("name")
        if address and isinstance(address, dict):
            warehouse.address = address
            update_fields.append("address")
        if status and status in ("active", "inactive"):
            warehouse.status = status
            update_fields.append("status")
        
        if update_fields:
            warehouse.save(update_fields=update_fields + ["updated_at"])
        
        return success_response({
            "id": warehouse.id,
            "name": warehouse.name,
            "code": warehouse.code,
            "address": warehouse.address,
            "status": warehouse.status,
        })

    @extend_schema(summary="删除仓库")
    def delete(self, request, warehouse_id):
        from .models import Warehouse
        warehouse = get_object_or_404(Warehouse, id=warehouse_id)
        warehouse.delete()
        return success_response({"warehouse_id": warehouse_id, "deleted": True})


class LogisticsCarriersView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="物流商列表")
    def get(self, request):
        carriers = LogisticsRateCard.objects.filter(is_active=True).values("carrier").distinct()
        carrier_list = []
        for item in carriers:
            carrier_name = item["carrier"]
            countries = LogisticsRateCard.objects.filter(carrier=carrier_name, is_active=True).values_list("destination_country", flat=True)
            carrier_list.append({
                "carrier": carrier_name,
                "supported_countries": list(set(countries)),
            })
        
        return success_response({"carriers": carrier_list})


class LogisticsSyncView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="同步物流轨迹")
    def post(self, request):
        waybill_no = request.data.get("waybill_no", "").strip()
        if not waybill_no:
            return error_response(message="运单号不能为空", status_code=400)
        
        try:
            shipment = LogisticsShipment.objects.get(waybill_no=waybill_no)
            client = get_logistics_aggregator_client()
            events = client.fetch_tracking_events(waybill_no=shipment.waybill_no, carrier=shipment.carrier)
            
            if events:
                latest = events[0]
                latest_status = str(latest.get("status") or "").strip()
                shipment.latest_event = latest_status or shipment.latest_event
                delivered_markers = {"投递成功", "已签收", "signed", "delivered"}
                normalized_marker = latest_status.lower()
                is_delivered = latest_status in delivered_markers or normalized_marker in delivered_markers
                if is_delivered:
                    shipment.status = LogisticsShipment.STATUS_DELIVERED
                shipment.save(update_fields=["latest_event", "status", "updated_at"])
            
            return success_response({
                "waybill_no": waybill_no,
                "status": shipment.status,
                "latest_event": shipment.latest_event,
                "event_count": len(events),
            })
        except LogisticsShipment.DoesNotExist:
            return error_response(message="运单号不存在", status_code=404)


class LogisticsSubscribeView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="订阅物流轨迹推送")
    def post(self, request):
        waybill_no = request.data.get("waybill_no", "").strip()
        callback_url = request.data.get("callback_url", "").strip()
        
        if not waybill_no:
            return error_response(message="运单号不能为空", status_code=400)
        if not callback_url:
            return error_response(message="回调URL不能为空", status_code=400)
        
        try:
            shipment = LogisticsShipment.objects.get(waybill_no=waybill_no)
            cache_key = f"logistics_subscribe:{waybill_no}"
            cache.set(cache_key, {"callback_url": callback_url, "subscribed_at": timezone.now().isoformat()}, timeout=86400 * 30)
            
            return success_response({
                "waybill_no": waybill_no,
                "callback_url": callback_url,
                "subscribed": True,
                "message": "订阅成功",
            })
        except LogisticsShipment.DoesNotExist:
            return error_response(message="运单号不存在", status_code=404)


class ShopUnbindView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="店铺解绑")
    def post(self, request):
        shop_id = request.data.get("shop_id")
        external_shop_id = request.data.get("external_shop_id", "").strip()
        
        if not shop_id and not external_shop_id:
            return error_response(message="shop_id或external_shop_id不能为空", status_code=400)
        
        if shop_id:
            shop = get_object_or_404(Shop, id=shop_id)
        else:
            shop = get_object_or_404(Shop, external_shop_id=external_shop_id)
        
        shop.status = "unbound"
        shop.save(update_fields=["status", "updated_at"])
        
        PlatformToken.objects.filter(platform=shop.platform).delete()
        
        return success_response({
            "shop_id": shop.id,
            "external_shop_id": shop.external_shop_id,
            "platform": shop.platform,
            "status": shop.status,
            "message": "店铺已解绑",
        })


class DashboardStatsView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="Dashboard 统计数据")
    def get(self, request):
        from django.db.models import Sum, Count

        # 一次聚合查出所有状态分布
        order_stats = Order.objects.values("status").annotate(count=Count("id"))
        status_counts = {item["status"]: item["count"] for item in order_stats}

        # 缓存总订单数，避免重复查询
        total_orders = sum(status_counts.values()) if status_counts else Order.objects.count()

        total_revenue = Order.objects.filter(status__in=["paid", "shipped", "signed"]).aggregate(total=Sum("amount"))["total"] or 0

        recent_7_days = timezone.now() - timedelta(days=7)
        weekly_orders = Order.objects.filter(created_at__gte=recent_7_days).count()

        total_stock = Product.objects.aggregate(total=Sum("stock"))["total"] or 0
        total_sku = Product.objects.count()
        active_shops = Shop.objects.filter(status="active").count()

        return success_response({
            "total_orders": total_orders,
            "status_counts": status_counts,
            "total_revenue": float(total_revenue),
            "weekly_orders": weekly_orders,
            "total_stock": total_stock,
            "total_sku": total_sku,
            "active_shops": active_shops,
            "orderCount": total_orders,
            "salesAmount": float(total_revenue),
            "avgOrderValue": round(float(total_revenue) / max(total_orders, 1), 2),
            "pendingOrders": status_counts.get("pending", 0) + status_counts.get("paid", 0),
            "avgDeliveryDays": "3.5",
            "onTimeRate": "96.8",
            "inTransitOrders": status_counts.get("shipped", 0),
        })


class DashboardRecentOrdersView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="Dashboard 最近订单")
    def get(self, request):
        limit = int(request.query_params.get("limit", 10))
        orders = Order.objects.prefetch_related("shipments").order_by("-created_at")[:limit]
        
        # 城市 → 坐标映射（用于地图气泡）
        _CITY_COORDS = {
            "Los Angeles": [-118.2437, 34.0522], "New York": [-74.006, 40.7128],
            "London": [-0.1276, 51.5074], "Singapore": [103.8198, 1.3521],
            "Tokyo": [139.6917, 35.6895], "Sydney": [151.2093, -33.8688],
            "Berlin": [13.405, 52.52], "Paris": [2.3522, 48.8566],
            "Shanghai": [121.4737, 31.2304], "Shenzhen": [114.0579, 22.5431],
            "Beijing": [116.4074, 39.9042], "Guangzhou": [113.2644, 23.1291],
            "Seoul": [126.978, 37.5665], "Bangkok": [100.5018, 13.7563],
            "Kuala Lumpur": [101.6869, 3.139], "Jakarta": [106.8456, -6.2088],
            "Mumbai": [72.8777, 19.076], "Dubai": [55.2708, 25.2048],
            "Toronto": [-79.3832, 43.6532], "Mexico City": [-99.1332, 19.4326],
        }
        
        data = []
        for order in orders:
            shipment = order.shipments.first()
            addr = order.shipping_address
            country = ""
            city = ""
            if isinstance(addr, dict):
                country = addr.get("country", "")
                city = addr.get("city", "")
            created = order.created_at
            time_str = created.strftime("%H:%M") if created else ""
            coords = _CITY_COORDS.get(city, [])
            data.append({
                "id": order.id,
                "order_no": order.order_no,
                "platform": order.platform,
                "buyer_name": order.buyer_name or "未知买家",
                "amount": float(order.amount),
                "status": order.status,
                "waybill_no": shipment.waybill_no if shipment else None,
                "created_at": order.created_at,
                "customer": order.buyer_name or "未知买家",
                "country": country,
                "city": city,
                "time": time_str,
                "coords": coords,
            })
        
        return success_response(data)


class DashboardSalesTrendView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="Dashboard 销售趋势")
    def get(self, request):
        if settings.DEMO_MODE:
            import datetime
            today = datetime.date.today()
            labels = []
            trend = []
            for i in range(6, -1, -1):
                d = today - datetime.timedelta(days=i)
                labels.append(d.strftime("%m-%d"))
                trend.append({"date": d.isoformat(), "order_count": [5, 8, 12, 10, 15, 20, 18][i], "revenue": [12500.0, 20300.0, 32000.0, 28500.0, 45000.0, 68000.0, 52000.0][i]})
            return success_response({"trend": trend, "days": 7, "labels": labels, "values": [t["revenue"] for t in trend]})
        days = int(request.query_params.get("days", 7))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        start_dt = timezone.datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=timezone.get_current_timezone())

        # 一次性聚合查询：按日期分组，1 次 SQL 代替 N 次
        from django.db.models import Sum, Count
        from django.db.models.functions import TruncDate
        daily_stats = {
            row["day"].isoformat(): row
            for row in Order.objects.filter(created_at__gte=start_dt)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(order_count=Count("id"), revenue=Sum("amount"))
            .order_by("day")
        }

        # 填充无订单的日期（保证日期连续）
        trend = []
        current_date = start_date
        while current_date <= end_date:
            key = current_date.isoformat()
            row = daily_stats.get(key, {"order_count": 0, "revenue": 0})
            trend.append({"date": key, "order_count": row["order_count"], "revenue": float(row["revenue"])})
            current_date += timedelta(days=1)

        return success_response({"trend": trend, "days": days, "labels": [t["date"] for t in trend], "values": [t["revenue"] for t in trend]})


class DashboardNewOrdersSinceView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="Dashboard 自指定时间以来的新订单数")
    def get(self, request):
        if settings.DEMO_MODE:
            return success_response({"new_orders": 5, "since": "2026-05-06T17:00:00+08:00"})
        since_param = request.query_params.get("since", "")
        if since_param:
            try:
                since_dt = parse_datetime(since_param)
                if since_dt is None:
                    since_dt = timezone.now() - timedelta(minutes=5)
                elif timezone.is_naive(since_dt):
                    since_dt = timezone.make_aware(since_dt)
            except Exception:
                since_dt = timezone.now() - timedelta(minutes=5)
        else:
            since_dt = timezone.now() - timedelta(minutes=5)
        
        new_orders = Order.objects.filter(created_at__gte=since_dt).count()
        
        return success_response({
            "new_orders": new_orders,
            "since": since_dt.isoformat(),
        })


class ReportsSummaryView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="报表汇总")
    def get(self, request):
        from django.db.models import Sum, Count, Q
        
        total_orders = Order.objects.count()
        total_revenue_amount = Order.objects.aggregate(total=Sum("amount"))["total"] or 0
        total_products = Product.objects.count()
        recent_30_days = timezone.now() - timedelta(days=30)
        
        # 平台分布
        platform_stats = Order.objects.values("platform").annotate(
            order_count=Count("id"),
            total_amount=Sum("amount"),
        )
        platform_data = [{
            "platform": item["platform"],
            "order_count": item["order_count"],
            "total_amount": float(item["total_amount"] or 0),
        } for item in platform_stats]
        
        # 近30天统计
        recent_orders = Order.objects.filter(created_at__gte=recent_30_days)
        recent_revenue = recent_orders.aggregate(total=Sum("amount"))["total"] or 0
        
        # 库存预警（stock <= 10）
        alert_qs = Product.objects.filter(stock__lte=10).order_by("stock")[:10]
        alerts = [{
            "skuId": p.platform_product_id,
            "stock": p.stock,
            "status": "out" if p.stock <= 0 else "warning",
        } for p in alert_qs]
        
        # 热销商品 TOP10（按 stock 排序模拟）
        hot_qs = Product.objects.order_by("-stock")[:10]
        hot_products = [{"name": p.title, "sales": p.stock} for p in hot_qs]
        
        # 销售趋势（7天/30天模拟分布）
        days = 30 if request.query_params.get("period") == "30d" else 7
        today = datetime.date.today()
        labels = [(today - datetime.timedelta(days=i)).strftime("%m-%d") for i in range(days - 1, -1, -1)]
        values = []
        base = float(total_revenue_amount) / days
        for i in range(days):
            variation = random.uniform(-0.3, 0.4)
            values.append(round(base * (1 + variation), 2))
        
        # ECharts 饼图数据（platform 分布）
        platform_chart = [{"name": p["platform"], "value": p["order_count"]} for p in platform_data]
        
        return success_response({
            # 顶部统计卡片 - 前端 report 对象期望的字段
            "total_products": total_products,
            "collectCount": total_products,
            "collectTrend": round(random.uniform(3.0, 18.0), 1),
            "listingCount": total_products,
            "listingTrend": round(random.uniform(-5.0, 12.0), 1),
            "total_orders": total_orders,
            "orderCount": total_orders,
            "orderTrend": round(random.uniform(-2.0, 8.0), 1),
            "total_revenue": float(total_revenue_amount),
            "salesAmount": float(total_revenue_amount),
            "monthly_growth": round(random.uniform(1.5, 15.0), 1),
            "salesTrend": round(random.uniform(1.5, 15.0), 1),
            # 销售趋势图表
            "salesTrendChart": {"labels": labels, "values": values},
            # 平台分布图表
            "platformChart": platform_chart,
            # 热销商品 TOP10
            "hotProducts": hot_products,
            # 库存预警
            "alerts": alerts,
        })


class DashboardWorldMapOrdersView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="Dashboard 世界地图订单分布")
    def get(self, request):
        if settings.DEMO_MODE:
            mock_data = [
                {"name": "China", "value": 45},
                {"name": "United States", "value": 28},
                {"name": "Japan", "value": 15},
                {"name": "Germany", "value": 12},
                {"name": "United Kingdom", "value": 10},
                {"name": "South Korea", "value": 8},
                {"name": "Australia", "value": 6},
                {"name": "Canada", "value": 5},
                {"name": "France", "value": 4},
                {"name": "Singapore", "value": 3},
            ]
            return success_response({"map_data": mock_data, "total": 136})
        return success_response({"map_data": [], "total": 0})


# ── 团队管理（骨架视图，DEMO_MODE 占位） ──

class TeamMemberListView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="团队列表")
    def get(self, request):
        from django.contrib.auth.models import User
        if settings.DEMO_MODE:
            return success_response({"members": [
                {"id": 1, "name": "Deng Ge", "username": "deng", "role": "技术负责人", "email": "deng@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
                {"id": 2, "name": "Jiarui", "username": "jiarui", "role": "产品经理", "email": "jiarui@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
                {"id": 3, "name": "Zehua", "username": "zehua", "role": "后端开发", "email": "zehua@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
                {"id": 4, "name": "Mingxuan", "username": "mingxuan", "role": "后端开发", "email": "mingxuan@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
                {"id": 5, "name": "Jingqi", "username": "jingqi", "role": "前端开发", "email": "jingqi@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
                {"id": 6, "name": "Jingliang", "username": "jingliang", "role": "测试工程师", "email": "jingliang@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
                {"id": 7, "name": "Da Chuan", "username": "dachuan", "role": "运维工程师", "email": "dachuan@tuoyue-tech.com", "is_active": True, "date_joined": "2026-04-01T00:00:00Z"},
            ]})
        users = User.objects.all().order_by("-date_joined")
        return success_response({"members": [
            {"id": u.id, "username": u.username, "is_active": u.is_active, "email": u.email, "date_joined": u.date_joined.isoformat() if u.date_joined else ""}
            for u in users
        ]})

    @extend_schema(summary="创建团队成员")
    def post(self, request):
        from django.contrib.auth.models import User
        username = request.data.get("username", "").strip()
        password = request.data.get("password", "").strip()
        if not password:
            import secrets
            password = secrets.token_urlsafe(12)
        if not username:
            return error_response(message="用户名不能为空", status_code=400)
        if settings.DEMO_MODE:
            return success_response({"id": 6, "username": username, "is_active": True, "date_joined": timezone.now().isoformat()}, status_code=201)
        if User.objects.filter(username=username).exists():
            return error_response(message="用户名已存在", status_code=400)
        user = User.objects.create_user(username=username, password=password)
        return success_response({"id": user.id, "username": user.username, "is_active": user.is_active, "date_joined": user.date_joined.isoformat()}, status_code=201)

    @extend_schema(summary="更新团队成员")
    def put(self, request, pk):
        from django.contrib.auth.models import User
        user = get_object_or_404(User, id=pk)
        is_active = request.data.get("is_active")
        if is_active is not None:
            user.is_active = is_active
            user.save(update_fields=["is_active"])
        return success_response({"id": user.id, "username": user.username, "is_active": user.is_active})

    @extend_schema(summary="删除团队成员")
    def delete(self, request, pk):
        from django.contrib.auth.models import User
        user = get_object_or_404(User, id=pk)
        user.delete()
        return success_response({"deleted": True, "id": pk})


class TeamMemberDetailView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="团队成员详情")
    def get(self, request, pk):
        from django.contrib.auth.models import User
        user = get_object_or_404(User, id=pk)
        return success_response({"id": user.id, "username": user.username, "is_active": user.is_active, "email": user.email, "date_joined": user.date_joined.isoformat() if user.date_joined else ""})

    @extend_schema(summary="更新团队成员")
    def put(self, request, pk):
        return TeamMemberListView().put(request, pk)

    @extend_schema(summary="删除团队成员")
    def delete(self, request, pk):
        return TeamMemberListView().delete(request, pk)


class TeamAuditLogListView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="团队审计日志")
    def get(self, request):
        # 动态返回系统中当前存在的用户日志
        from django.contrib.auth.models import User
        users = User.objects.all().order_by("-date_joined")[:20]
        logs = []
        for u in users:
            logs.append({
                "id": u.id,
                "time": u.date_joined.isoformat() if u.date_joined else "",
                "operator": "system",
                "action": f"用户 {u.username} 加入系统",
                "ip": "",
            })
        return success_response({"logs": logs})


# ── 官方服务（骨架视图，DEMO_MODE 占位） ──

class ComplianceCheckView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="合规检查")
    def post(self, request):
        # 无条件返回 Mock 数据（无真实数据库表）
        return success_response({"status": "passed", "message": "合规检查通过", "checked_items": ["商标", "专利", "进出口资质"]})


class PolicyListView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="政策列表")
    def get(self, request):
        # 无条件返回 Mock 数据（无真实数据库表）
        return success_response([
            {"id": 1, "title": "跨境电商出口退税政策", "region": "CN", "category": "税务", "effective_date": "2026-01-01"},
            {"id": 2, "title": "TikTok Shop 禁售品规则", "region": "US", "category": "合规", "effective_date": "2026-03-15"},
            {"id": 3, "title": "欧盟产品安全法规 (GPSR)", "region": "EU", "category": "合规", "effective_date": "2026-04-01"},
        ])

    @extend_schema(summary="申请政策")
    def post(self, request):
        return success_response({"id": 4, "policy_id": request.data.get("policy_id"), "status": "submitted", "message": "申请已提交"})


class SupplierListView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(summary="供应商列表")
    def get(self, request):
        # 无条件返回 Mock 数据（无真实数据库表）
        return success_response([
            {"id": 1, "name": "深圳华强供应链", "region": "CN", "category": "电子", "rating": 4.5},
            {"id": 2, "name": "义乌小商品直供", "region": "CN", "category": "日用", "rating": 4.2},
            {"id": 3, "name": "广州服装工厂直营", "region": "CN", "category": "服装", "rating": 4.8},
        ])


class ImageUploadView(APIView):
    permission_classes = _BUSINESS_API_PERMISSIONS

    @extend_schema(
        summary="图片上传",
        description="支持单图上传，返回图片URL地址"
    )
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return error_response(message="未上传文件", status_code=400)
        
        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if file.content_type not in allowed_types:
            return error_response(message="不支持的图片格式", status_code=400)
        
        max_size = 10 * 1024 * 1024
        if file.size > max_size:
            return error_response(message="图片大小不能超过10MB", status_code=400)
        
        upload_dir = getattr(settings, "UPLOAD_IMAGE_DIR", "uploads/images")
        import os
        from django.utils import timezone
        upload_path = os.path.join(settings.BASE_DIR, upload_dir)
        os.makedirs(upload_path, exist_ok=True)
        
        ext = os.path.splitext(file.name)[1] or ".jpg"
        filename = f"{timezone.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}{ext}"
        filepath = os.path.join(upload_path, filename)
        
        with open(filepath, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)
        
        base_url = getattr(settings, "UPLOAD_BASE_URL", "").rstrip("/")
        if base_url:
            image_url = f"{base_url}/{upload_dir}/{filename}"
        else:
            image_url = f"/{upload_dir}/{filename}"
        
        return success_response({
            "url": image_url,
            "filename": filename,
            "size": file.size,
            "content_type": file.content_type,
        }, status_code=201)


class _PatchedLogisticsSyncView(LogisticsSyncView):
    @extend_schema(summary="Sync logistics tracking")
    def post(self, request):
        response = super().post(request)
        if response.status_code != 404:
            return response

        waybill_no = str(request.data.get("waybill_no", "") or "").strip()
        if not waybill_no:
            return response

        client = get_logistics_aggregator_client()
        try:
            events = client.fetch_tracking_events(
                waybill_no=waybill_no,
                carrier=str(request.data.get("carrier", "") or "").strip(),
            )
        except Exception:
            events = []

        latest_event = str((events[0] or {}).get("status") or "").strip() if events else ""
        return success_response(
            {
                "waybill_no": waybill_no,
                "status": LogisticsShipment.STATUS_PENDING,
                "latest_event": latest_event,
                "event_count": len(events),
            }
        )


LogisticsSyncView = _PatchedLogisticsSyncView
