#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${AIRFLOW_HOME}"

export AIRFLOW__WEBSERVER__WEB_SERVER_HOST=0.0.0.0
export AIRFLOW__WEBSERVER__WEB_SERVER_PORT="${PORT:-10000}"

exec airflow standalone
