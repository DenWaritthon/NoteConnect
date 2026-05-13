"""Tests for no-sudo runtime scripts and deploy readiness checks."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from scripts.check_db_ready import main as check_db_ready_main
from scripts.check_model_ready import main as check_model_ready_main
from scripts.check_deploy_ready import run_checks
from src.core.logging import configure_logging
from src.core.model_readiness import check_model_files, is_git_lfs_pointer


class OperabilityTests(unittest.TestCase):
    def test_run_server_uses_single_worker_without_reload(self) -> None:
        script = (BACKEND_DIR / "scripts" / "run_server.sh").read_text()

        self.assertIn("--workers 1", script)
        self.assertNotIn("--reload", script)
        self.assertIn("APP_HOST", script)
        self.assertIn("APP_PORT", script)
        self.assertIn('source ".env"', script)

    def test_nohup_scripts_use_runtime_pid_and_log_files(self) -> None:
        start_script = (BACKEND_DIR / "scripts" / "start_nohup.sh").read_text()
        stop_script = (BACKEND_DIR / "scripts" / "stop_nohup.sh").read_text()

        self.assertIn("runtime", start_script)
        self.assertIn("noteconnect.pid", start_script)
        self.assertIn("noteconnect.log", start_script)
        self.assertIn("kill -0", start_script)
        self.assertIn("noteconnect.pid", stop_script)
        self.assertIn("kill \"${PID}\"", stop_script)

    def test_check_deploy_ready_reports_expected_runtime_settings(self) -> None:
        env = {
            "API_SECRET_KEY": "test-secret",
            "APP_HOST": "127.0.0.1",
            "APP_PORT": "8000",
            "ENABLE_DOCS": "false",
            "READY_CHECK_DATABASE": "false",
            "LOG_LEVEL": "INFO",
            "LOG_REQUESTS": "true",
            "SLOW_REQUEST_MS": "3000",
            "EXPLANATION_LOAD_MODE": "lazy",
        }
        with patch.dict(os.environ, env, clear=True):
            with patch("src.core.config.load_env_file"):
                results = run_checks()

        pairs = {(result.level, result.label) for result in results}
        self.assertIn(("PASS", "API_SECRET_KEY"), pairs)
        self.assertIn(("PASS", "APP_HOST"), pairs)
        self.assertIn(("PASS", "APP_PORT"), pairs)
        self.assertIn(("PASS", "EXPLANATION_LOAD_MODE"), pairs)
        self.assertIn(("PASS", "LOG_REQUESTS"), pairs)
        self.assertIn(("PASS", "SLOW_REQUEST_MS"), pairs)
        self.assertIn(("WARN", "READY_CHECK_DATABASE"), pairs)

    def test_index_sql_contains_expected_baseline_indexes(self) -> None:
        index_sql = (BACKEND_DIR / "database" / "create_index.sql").read_text()

        self.assertIn("idx_noteconnect_folder_active_open", index_sql)
        self.assertIn("idx_noteconnect_note_active_folder_created", index_sql)
        self.assertIn("USING hnsw (sentence_embedding vector_cosine_ops)", index_sql)
        self.assertIn("idx_noteconnect_relation_active_folder_created", index_sql)
        self.assertIn("idx_noteconnect_evidence_active_relation_created", index_sql)

    def test_check_db_ready_returns_zero_when_database_is_reachable(self) -> None:
        with patch("scripts.check_db_ready.get_config", return_value=object()):
            with patch("scripts.check_db_ready.check_database_connection"):
                with redirect_stdout(StringIO()) as output:
                    exit_code = check_db_ready_main()

        self.assertEqual(exit_code, 0)
        self.assertIn("PASS DB readiness check passed", output.getvalue())

    def test_check_db_ready_returns_one_when_database_is_unreachable(self) -> None:
        with patch("scripts.check_db_ready.get_config", return_value=object()):
            with patch(
                "scripts.check_db_ready.check_database_connection",
                side_effect=RuntimeError("connection refused"),
            ):
                with redirect_stdout(StringIO()) as output:
                    exit_code = check_db_ready_main()

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL DB readiness check failed", output.getvalue())

    def test_model_readiness_detects_git_lfs_pointer_weight(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            weight_file = model_dir / "model.safetensors"
            weight_file.write_text(
                "version https://git-lfs.github.com/spec/v1\n"
                "oid sha256:abc\n"
                "size 123\n"
            )

            result = check_model_files("embedding", str(model_dir))

        self.assertFalse(result.ok)
        self.assertIn("Git LFS pointer", result.detail)

    def test_model_readiness_detects_missing_local_path(self) -> None:
        result = check_model_files("embedding", "./model/not-found-for-test")

        self.assertFalse(result.ok)
        self.assertIn("does not exist", result.detail)

    def test_is_git_lfs_pointer_returns_false_for_binary_like_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            weight_file = Path(temp_dir) / "model.safetensors"
            weight_file.write_bytes(b"not-a-pointer")

            self.assertFalse(is_git_lfs_pointer(weight_file))

    def test_check_model_ready_returns_one_when_file_check_fails(self) -> None:
        fake_config = type(
            "FakeConfig",
            (),
            {
                "embedding_model": "./model/missing-embedding",
                "nli_model": "./model/missing-nli",
                "explanation_model": "./model/missing-explanation",
            },
        )()

        with patch("scripts.check_model_ready.get_config", return_value=fake_config):
            with redirect_stdout(StringIO()) as output:
                exit_code = check_model_ready_main(["--skip-load"])

        self.assertEqual(exit_code, 1)
        self.assertIn("FAIL embedding files", output.getvalue())

    def test_check_model_ready_returns_zero_when_file_and_load_checks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            model_dir = Path(temp_dir)
            (model_dir / "model.safetensors").write_bytes(b"real-ish")
            fake_config = type(
                "FakeConfig",
                (),
                {
                    "embedding_model": str(model_dir),
                    "nli_model": str(model_dir),
                    "explanation_model": str(model_dir),
                },
            )()

            with patch("scripts.check_model_ready.get_config", return_value=fake_config):
                with patch(
                    "scripts.check_model_ready.verify_model_loads",
                    return_value=[
                        ("embedding load", True, "loaded"),
                        ("nli load", True, "loaded"),
                        ("explanation load", True, "loaded"),
                    ],
                ):
                    with redirect_stdout(StringIO()) as output:
                        exit_code = check_model_ready_main([])

        self.assertEqual(exit_code, 0)
        self.assertIn("PASS explanation load", output.getvalue())

    def test_configure_logging_accepts_known_level(self) -> None:
        configure_logging("INFO")


if __name__ == "__main__":
    unittest.main()
