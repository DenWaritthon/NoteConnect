"""Check whether the configured PostgreSQL database is reachable."""

from __future__ import annotations

import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.core.config import get_config
from src.core.database import check_database_connection


def main() -> int:
    try:
        config = get_config()
        check_database_connection(config)
    except Exception as error:
        print(f"FAIL DB readiness check failed: {error}")
        return 1

    print("PASS DB readiness check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
