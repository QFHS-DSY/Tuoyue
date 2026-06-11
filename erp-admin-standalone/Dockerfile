# ============================================================
# 前端 Dockerfile - 多阶段构建
# 构建阶段：Node 编译 → 运行阶段：Nginx Alpine 轻量服务
# ============================================================

# ── 构建阶段 ──────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /build

COPY package*.json ./
RUN npm ci --only=production --no-audit --no-fund

COPY . .
RUN npm run build

# ── 运行阶段 ──────────────────────────────────────────────
FROM nginx:1.27-alpine

# 安全：移除无用工具
RUN rm -f /usr/sbin/ping /usr/sbin/wget /usr/sbin/curl /usr/bin/gettext /usr/bin/envsubst

# 复制构建产物
COPY --from=builder /build/dist /usr/share/nginx/html

# Nginx 配置：SPA 路由回退 + API 代理
RUN echo 'server { \
    listen       1101; \
    server_name  localhost; \
    root   /usr/share/nginx/html; \
    index  index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api/ { \
        proxy_pass http://backend:1102; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 1101

USER nginx

CMD ["nginx", "-g", "daemon off;"]
