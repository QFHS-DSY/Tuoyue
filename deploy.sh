#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="${ROOT_DIR}/docker-compose.prod.yml"

required_envs=(
  DJANGO_SECRET_KEY
  MYSQL_ROOT_PASSWORD
  MYSQL_DATABASE
  MYSQL_USER
  MYSQL_PASSWORD
  FERNET_KEY
)

for name in "${required_envs[@]}"; do
  if [[ -z "${!name:-}" ]]; then
    echo "Missing required environment variable: ${name}" >&2
    exit 1
  fi
done

export CELERY_WORKER_CONCURRENCY="${CELERY_WORKER_CONCURRENCY:-4}"
export MYSQL_INNODB_BUFFER_POOL_SIZE="${MYSQL_INNODB_BUFFER_POOL_SIZE:-4G}"

compose() {
  docker compose -f "${COMPOSE_FILE}" "$@"
}

container_health() {
  local service="$1"
  local container_id
  container_id="$(compose ps -q "${service}")"
  if [[ -z "${container_id}" ]]; then
    echo "missing"
    return 0
  fi
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "${container_id}"
}

wait_for_healthy() {
  local service="$1"
  local timeout_seconds="$2"
  local waited=0

  until [[ "$(container_health "${service}")" == "healthy" ]]; do
    if (( waited >= timeout_seconds )); then
      echo "Service ${service} did not become healthy within ${timeout_seconds}s" >&2
      compose logs --tail 50 "${service}" >&2 || true
      exit 1
    fi
    sleep 5
    waited=$((waited + 5))
  done
}

echo "[1/4] Building production images"
compose build backend celery-worker celery-beat

echo "[2/4] Starting stateful services"
compose up -d mysql redis
wait_for_healthy mysql 180
wait_for_healthy redis 60

echo "[3/4] Running migrations"
compose run --rm backend python manage.py migrate

echo "[4/4] Starting application services"
compose up -d backend celery-worker celery-beat
wait_for_healthy backend 120
wait_for_healthy celery-worker 60
wait_for_healthy celery-beat 60

compose ps
