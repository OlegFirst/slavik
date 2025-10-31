#!/usr/bin/env bash
set -euo pipefail

# --- Startup lock to prevent concurrent initialization ---
LOCK_FILE="/var/lib/odoo/startup.lock"
if [ -f "$LOCK_FILE" ]; then
  echo "[entrypoint] Another Odoo process is initializing. Waiting..."
  while [ -f "$LOCK_FILE" ]; do
    sleep 5
  done
  echo "[entrypoint] Lock released, continuing..."
fi
touch "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# --- проверяем и доустанавливаем Python зависимости ---
if [ -f /check_dependencies.sh ]; then
  echo "[entrypoint] Checking Python dependencies..."
  /check_dependencies.sh
fi

# --- нормализуем ENV (дефолты) ---
DB_HOST="${DB_HOST:-postgres}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-odoo}"
DB_PASSWORD="${DB_PASSWORD:-odoo123}"
DB_NAME="${DB_NAME:-bcm_platform}"
HTTP_PORT="${PORT:-8069}"

echo "[entrypoint] DB=${DB_USER}@${DB_HOST}:${DB_PORT}/${DB_NAME}  http=${HTTP_PORT}"

# --- ждём Postgres (без nc) ---
for i in {1..60}; do
  (echo > /dev/tcp/"${DB_HOST}"/"${DB_PORT}") >/dev/null 2>&1 && { echo "[entrypoint] PG is up"; break; }
  sleep 1
done

# --- ждём Redis (если задан) ---
if [[ -n "${REDIS_HOST:-}" ]] && [[ "${REDIS_HOST}" != "" ]]; then
  echo "[entrypoint] wait Redis at ${REDIS_HOST}:${REDIS_PORT:-6379}"
  # Пропускаем проверку если нет redis-cli
  if command -v redis-cli &> /dev/null; then
    for i in {1..60}; do
      redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT:-6379}" ping >/dev/null 2>&1 && { echo "[entrypoint] Redis is up"; break; }
      sleep 1
    done
  else
    echo "[entrypoint] redis-cli not found, skipping Redis check"
  fi
fi

# --- опционально: дождаться AI Orchestrator (если задан URL) ---
if [[ -n "${AI_ORCHESTRATOR_URL:-}" ]]; then
  echo "[entrypoint] wait AI ${AI_ORCHESTRATOR_URL}/health"
  for i in {1..60}; do
    curl -fsS "${AI_ORCHESTRATOR_URL%/}/health" >/dev/null 2>&1 && { echo "[entrypoint] AI is up"; break; }
    sleep 2
  done
fi

# --- (опция) создать БД, если у роли есть CREATEDB ---
if [[ "${ODOO_CREATEDB:-0}" == "1" ]]; then
  echo "[entrypoint] ensure DB ${DB_NAME}"
  PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -tc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" \
    | grep -q 1 || PGPASSWORD="${DB_PASSWORD}" psql -h "${DB_HOST}" -U "${DB_USER}" -d postgres -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};" || true
fi

# --- единовременная инициализация base (без падений при повторе) ---
if [[ "${ODOO_INIT_BASE:-1}" == "1" ]]; then
  echo "[entrypoint] install/upgrade base in ${DB_NAME}"
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i base --without-demo=all --stop-after-init || true
fi

# --- (опция) обновить все модули один раз ---
if [[ "${ODOO_UPGRADE_ALL:-0}" == "1" ]]; then
  echo "[entrypoint] upgrade all modules in ${DB_NAME}"
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -u all --stop-after-init || true
fi

# --- установка BCM модулей поэтапно ---
if [[ "${ODOO_INSTALL_BCM_CORE:-1}" == "1" ]]; then
  echo "[entrypoint] installing BCM foundation modules in ${DB_NAME}"
  
  # Сначала устанавливаем базовые зависимости Odoo
  echo "[entrypoint] installing base Odoo modules..."
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i web,mail \
    --without-demo=all --stop-after-init || true
  
  # Устанавливаем BCM модули поэтапно (по 5 за раз чтобы не висло)
  echo "[entrypoint] installing BCM modules stage 1/4..."
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i bcm_core,bcm_base,bcm_config,bcm_context,bcm_bia \
    --without-demo=all --stop-after-init || true
  
  echo "[entrypoint] installing BCM modules stage 2/4..."
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i bcm_risk_management,bcm_plans,bcm_templates,bcm_incident,bcm_incident_management \
    --without-demo=all --stop-after-init || true
  
  echo "[entrypoint] installing BCM modules stage 3/4..."
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i bcm_exercise,bcm_training,bcm_audit,bcm_governance,bcm_kpi \
    --without-demo=all --stop-after-init || true
  
  echo "[entrypoint] installing BCM modules stage 4/4..."
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i bcm_reporting,bcm_clients,bcm_portal,bcm_intelligent_base,bcm_scenario_hub \
    --without-demo=all --stop-after-init || true
    
  echo "[entrypoint] All BCM modules installed successfully!"
fi

# --- установка дополнительных BCM модулей (опционально) ---
if [[ -n "${ODOO_INSTALL_BCM_MODULES:-}" ]]; then
  echo "[entrypoint] installing additional BCM modules: ${ODOO_INSTALL_BCM_MODULES}"
  /usr/bin/odoo \
    --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
    --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
    -d "${DB_NAME}" -i "${ODOO_INSTALL_BCM_MODULES}" \
    --without-demo=all --stop-after-init || true
fi

# --- запуск HTTP сервера ---
exec /usr/bin/odoo \
  --http-port="${HTTP_PORT}" \
  --db_host="${DB_HOST}" --db_port="${DB_PORT}" \
  --db_user="${DB_USER}" --db_password="${DB_PASSWORD}" \
  --config=/etc/odoo/odoo.conf \
  --db-filter="^${DB_NAME}$" \
  ${PROXY_MODE:+--proxy-mode}
