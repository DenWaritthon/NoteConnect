"""Runtime configuration tests for production-oriented behavior."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.api.routers import health_router
from src.core.config import AppConfig, DatabaseConfig, get_config


def runtime_config(
    *,
    enable_docs: bool = True,
    ready_check_database: bool = False,
) -> AppConfig:
    return AppConfig(
        app_env="test",
        app_host="127.0.0.1",
        app_port=8000,
        enable_docs=enable_docs,
        ready_check_database=ready_check_database,
        log_level="INFO",
        database=DatabaseConfig(
            host="localhost",
            port=5432,
            name="noteconnect_test",
            user="postgres",
            password="",
            connect_timeout=7,
        ),
        api_secret_key="test-secret",
        api_key_header_name="X-API-Key",
        embedding_model="stub",
        nli_model="stub",
        explanation_model="stub",
        explanation_max_new_tokens=32,
        explanation_load_mode="lazy",
        embedding_dimension=3,
        similarity_threshold=0.4,
        threshold_scale=0.2,
        similarity_top_k=10,
        similar_word_threshold=0.55,
    )


class RuntimeConfigTests(unittest.TestCase):
    def test_get_config_reads_production_runtime_settings(self) -> None:
        env = {
            "APP_ENV": "production",
            "APP_HOST": "127.0.0.1",
            "APP_PORT": "18000",
            "ENABLE_DOCS": "false",
            "READY_CHECK_DATABASE": "true",
            "LOG_LEVEL": "debug",
            "DB_CONNECT_TIMEOUT": "7",
            "EXPLANATION_LOAD_MODE": "lazy",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("src.core.config.load_env_file"):
                config = get_config()

        self.assertEqual(config.app_env, "production")
        self.assertEqual(config.app_host, "127.0.0.1")
        self.assertEqual(config.app_port, 18000)
        self.assertFalse(config.enable_docs)
        self.assertTrue(config.ready_check_database)
        self.assertEqual(config.log_level, "DEBUG")
        self.assertEqual(config.database.connect_timeout, 7)
        self.assertEqual(config.explanation_load_mode, "lazy")

    def test_invalid_explanation_load_mode_fails_fast(self) -> None:
        with patch.dict(os.environ, {"EXPLANATION_LOAD_MODE": "disabled"}, clear=True):
            with patch("src.core.config.load_env_file"):
                with self.assertRaisesRegex(ValueError, "EXPLANATION_LOAD_MODE"):
                    get_config()

    def test_database_connect_kwargs_include_timeout(self) -> None:
        config = runtime_config()

        self.assertEqual(config.database.connect_kwargs["connect_timeout"], 7)

    def test_app_factory_can_disable_docs(self) -> None:
        import main

        with patch("main.get_config", return_value=runtime_config(enable_docs=False)):
            app = main.create_app()
        client = TestClient(app)

        self.assertEqual(client.get("/docs").status_code, 404)
        self.assertEqual(client.get("/openapi.json").status_code, 404)

    def test_ready_returns_503_when_database_check_fails(self) -> None:
        app = FastAPI()
        app.include_router(health_router.router)
        app.state.config = SimpleNamespace(
            ready_check_database=True,
            explanation_load_mode="lazy",
        )
        client = TestClient(app)

        with patch(
            "src.api.routers.health_router.check_database_connection",
            side_effect=RuntimeError("database unavailable"),
        ):
            response = client.get("/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Database is not ready."})


if __name__ == "__main__":
    unittest.main()
