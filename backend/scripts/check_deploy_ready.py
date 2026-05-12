"""Check whether the backend runtime is ready for a no-sudo private deploy."""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.core.config import get_config


@dataclass(frozen=True)
class CheckResult:
    level: str
    label: str
    detail: str


def pass_result(label: str, detail: str) -> CheckResult:
    return CheckResult("PASS", label, detail)


def warn_result(label: str, detail: str) -> CheckResult:
    return CheckResult("WARN", label, detail)


def fail_result(label: str, detail: str) -> CheckResult:
    return CheckResult("FAIL", label, detail)


def package_available(package_name: str) -> bool:
    return importlib.util.find_spec(package_name) is not None


def run_checks() -> list[CheckResult]:
    results: list[CheckResult] = []

    if sys.version_info >= (3, 12):
        results.append(pass_result("Python version", sys.version.split()[0]))
    else:
        results.append(fail_result("Python version", "Python 3.12 or newer is required."))

    env_path = BACKEND_DIR / ".env"
    if env_path.exists():
        results.append(pass_result(".env file", str(env_path)))
    else:
        results.append(warn_result(".env file", "backend/.env was not found."))

    try:
        config = get_config()
    except Exception as error:
        results.append(fail_result("Config load", str(error)))
        return results

    if config.api_secret_key:
        results.append(pass_result("API_SECRET_KEY", "configured"))
    else:
        results.append(fail_result("API_SECRET_KEY", "missing"))

    results.append(pass_result("APP_HOST", config.app_host))
    results.append(pass_result("APP_PORT", str(config.app_port)))
    results.append(pass_result("EXPLANATION_LOAD_MODE", config.explanation_load_mode))
    results.append(pass_result("DB_CONNECT_TIMEOUT", str(config.database.connect_timeout)))
    results.append(pass_result("LOG_LEVEL", config.log_level))
    results.append(pass_result("LOG_REQUESTS", str(config.log_requests).lower()))
    results.append(pass_result("SLOW_REQUEST_MS", str(config.slow_request_ms)))

    if config.app_env == "production" and config.enable_docs:
        results.append(warn_result("ENABLE_DOCS", "true in production"))
    else:
        results.append(pass_result("ENABLE_DOCS", str(config.enable_docs).lower()))

    if config.ready_check_database:
        results.append(pass_result("READY_CHECK_DATABASE", "true"))
    else:
        results.append(warn_result("READY_CHECK_DATABASE", "false; DB readiness is skipped"))

    for package_name in ("fastapi", "uvicorn", "torch", "transformers", "psycopg"):
        if package_available(package_name):
            results.append(pass_result(f"package:{package_name}", "available"))
        else:
            results.append(fail_result(f"package:{package_name}", "not installed"))

    try:
        import main

        if hasattr(main, "app"):
            results.append(pass_result("main:app import", "available"))
        else:
            results.append(fail_result("main:app import", "app was not found"))
    except Exception as error:
        results.append(fail_result("main:app import", str(error)))

    return results


def main() -> int:
    results = run_checks()
    for result in results:
        print(f"{result.level} {result.label}: {result.detail}")

    return 1 if any(result.level == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
