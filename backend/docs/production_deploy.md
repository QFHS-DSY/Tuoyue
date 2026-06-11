# Production Deploy

This repository now ships a production deployment path centered on:

- `backend/Dockerfile.prod`: multi-stage, non-root runtime image with a built-in HTTP healthcheck
- `docker-compose.prod.yml`: private MySQL and Redis, backend API, Celery worker, and Celery beat
- `deploy.sh`: idempotent bootstrap that builds images, starts stateful services, runs migrations, and waits for healthy containers

## Required environment variables

Export these before running `./deploy.sh`:

- `DJANGO_SECRET_KEY`
- `MYSQL_ROOT_PASSWORD`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `FERNET_KEY`

Recommended operational overrides:

- `BACKEND_PUBLISH_PORT`
- `ALLOWED_HOSTS`
- `BACKEND_PUBLIC_URL`
- `CELERY_WORKER_CONCURRENCY` (defaults to `4`)
- `MYSQL_INNODB_BUFFER_POOL_SIZE` (defaults to `4G`)
- `DEMO_MODE`

Optional third-party platform variables are listed in `backend/.env.example`.

## Deploy

```bash
chmod +x deploy.sh
./deploy.sh
```

## Health model

- `backend`: probes `http://127.0.0.1:8000/api/health/`
- `mysql`: native `mysqladmin ping`
- `redis`: native `redis-cli ping`
- `celery-worker`: process check via `pgrep`
- `celery-beat`: process check via `pgrep`
