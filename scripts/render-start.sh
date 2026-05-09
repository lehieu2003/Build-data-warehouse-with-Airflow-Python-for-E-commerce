#!/usr/bin/env bash
set -euo pipefail

echo "Starting Render Airflow entrypoint"

mkdir -p "${AIRFLOW_HOME}"

export AIRFLOW__WEBSERVER__WEB_SERVER_HOST=0.0.0.0
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="${PORT:-10000}"
export AIRFLOW__CORE__LOAD_EXAMPLES="${AIRFLOW__CORE__LOAD_EXAMPLES:-False}"
export _AIRFLOW_WWW_USER_USERNAME="${_AIRFLOW_WWW_USER_USERNAME:-airflow}"
export _AIRFLOW_WWW_USER_PASSWORD="${_AIRFLOW_WWW_USER_PASSWORD:-airflow}"

if [ ! -f "${AIRFLOW_HOME}/airflow.db" ]; then
  echo "Initializing Airflow metadata database"
  airflow db init

  echo "Creating Airflow admin user"
  airflow users create \
    --role Admin \
    --username "${_AIRFLOW_WWW_USER_USERNAME}" \
    --password "${_AIRFLOW_WWW_USER_PASSWORD}" \
    --firstname Airflow \
    --lastname Admin \
    --email admin@example.com || true
else
  echo "Existing Airflow metadata database found"
fi

echo "Starting Airflow webserver on port ${PORT:-10000}"
exec airflow webserver --hostname 0.0.0.0 --port "${PORT:-10000}"
