#!/usr/bin/env bash
set -euo pipefail

mkdir -p "${AIRFLOW_HOME}"

exec airflow standalone
