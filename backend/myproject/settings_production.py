# ============================================================
# 跨境电商ERP — 生产环境配置覆盖
# 继承 myproject.settings 并覆盖/补充生产所需配置
# 使用方式：DJANGO_SETTINGS_MODULE=myproject.settings_production
# ============================================================
import os
from pathlib import Path

from .settings import *  # noqa: F401, F403

BASE_DIR = Path(__file__).resolve().parent.parent

# ── 静态文件 ──
# collectstatic 输出目录，由 Nginx 直接服务
STATIC_ROOT = os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles"))

# ── 上传文件 ──
# 图片上传存储目录（通过 Nginx /uploads/ 路由对外服务）
UPLOAD_IMAGE_DIR = os.getenv("UPLOAD_IMAGE_DIR", "uploads/images")
UPLOAD_BASE_URL = os.getenv("UPLOAD_BASE_URL", "")

# ── Session 安全 ──
# 生产环境启用安全的 Cookie 设置
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True

# ── 安全配置 ──
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = False  # 由 Nginx 处理 HTTPS 重定向
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ── 日志 ──
# 生产环境下将所有日志同时输出到文件，便于集中采集
LOGGING["handlers"]["production_file"] = {  # noqa: F405
    "class": "logging.handlers.RotatingFileHandler",
    "filename": os.getenv("PROD_LOG_FILE", str(BASE_DIR / "logs" / "production.log")),
    "maxBytes": 50 * 1024 * 1024,  # 50MB
    "backupCount": 10,
    "formatter": "standard",
    "encoding": "utf-8",
}
LOGGING["root"]["handlers"].append("production_file")  # noqa: F405
