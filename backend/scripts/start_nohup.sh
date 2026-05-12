#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUNTIME_DIR="${BACKEND_DIR}/runtime"
PID_FILE="${RUNTIME_DIR}/noteconnect.pid"
LOG_FILE="${RUNTIME_DIR}/noteconnect.log"

mkdir -p "${RUNTIME_DIR}"

if [[ -f "${PID_FILE}" ]]; then
  PID="$(cat "${PID_FILE}")"
  if [[ -n "${PID}" ]] && kill -0 "${PID}" 2>/dev/null; then
    echo "NoteConnect backend is already running with PID ${PID}."
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

cd "${BACKEND_DIR}"

export TOKENIZERS_PARALLELISM="${TOKENIZERS_PARALLELISM:-false}"
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-1}"
export MKL_NUM_THREADS="${MKL_NUM_THREADS:-1}"

nohup bash "${SCRIPT_DIR}/run_server.sh" > "${LOG_FILE}" 2>&1 &
PID="$!"
echo "${PID}" > "${PID_FILE}"
echo "Started NoteConnect backend with PID ${PID}."
echo "Log file: ${LOG_FILE}"
