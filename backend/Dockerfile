# ============================================================
# 后端 Dockerfile - 多阶段构建
# 目标：镜像小、构建快、安全性好
# ============================================================

# ── 构建阶段 ──────────────────────────────────────────────
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ── 运行阶段 ──────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

# 安全：非 root 用户
RUN addgroup --system --gid 1001 erp && \
    adduser --system --uid 1001 --ingroup erp --home /app --shell /sbin/nologin erp

# 从构建阶段复制依赖
COPY --from=builder /root/.local /root/.local

WORKDIR /app

# 复制代码并设置权限
COPY --chown=erp:erp . .

USER erp

EXPOSE 1102

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import http.client; c=http.client.HTTPConnection('127.0.0.1',1102,timeout=3); c.request('GET','/api/health/'); assert c.getresponse().status<500"

CMD ["python", "-m", "uvicorn", "myproject.asgi:application", "--host", "0.0.0.0", "--port", "1102", "--workers", "2"]
