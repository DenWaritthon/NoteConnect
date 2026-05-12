#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
RUNTIME_DIR="${BACKEND_DIR}/runtime"
PID_FILE="${RUNTIME_DIR}/noteconnect.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "NoteConnect backend PID file was not found."
  exit 0
fi

PID="$(cat "${PID_FILE}")"
if [[ -z "${PID}" ]]; then
  rm -f "${PID_FILE}"
  echo "PID file was empty and has been removed."
  exit 0
fi

if kill -0 "${PID}" 2>/dev/null; then
  kill "${PID}"
  echo "Stopped NoteConnect backend with PID ${PID}."
else
  echo "No running process found for PID ${PID}."
fi

rm -f "${PID_FILE}"
