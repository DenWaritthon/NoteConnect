"""Check local model files and optional offline model loading before startup."""

from __future__ import annotations

import argparse
import gc
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.core.config import get_config
from src.core.model_readiness import check_configured_model_files, resolve_model_reference


def verify_model_loads(config) -> list[tuple[str, bool, str]]:
    """Load each configured model offline so startup errors are caught early."""
    import torch
    from sentence_transformers import CrossEncoder, SentenceTransformer
    from transformers import AutoModelForCausalLM, AutoTokenizer

    results: list[tuple[str, bool, str]] = []

    try:
        embedding_model = SentenceTransformer(
            resolve_model_reference(config.embedding_model),
            local_files_only=True,
        )
        del embedding_model
        gc.collect()
        results.append(("embedding load", True, "loaded"))
    except Exception as error:
        results.append(("embedding load", False, str(error)))

    try:
        nli_model = CrossEncoder(
            resolve_model_reference(config.nli_model),
            local_files_only=True,
        )
        del nli_model
        gc.collect()
        results.append(("nli load", True, "loaded"))
    except Exception as error:
        results.append(("nli load", False, str(error)))

    try:
        explanation_model = resolve_model_reference(config.explanation_model)
        tokenizer = AutoTokenizer.from_pretrained(
            explanation_model,
            local_files_only=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            explanation_model,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
            local_files_only=True,
        )
        del model
        del tokenizer
        gc.collect()
        results.append(("explanation load", True, "loaded"))
    except Exception as error:
        results.append(("explanation load", False, str(error)))

    return results


def run_checks(*, skip_load: bool = False) -> list[tuple[str, str, str]]:
    config = get_config()
    results: list[tuple[str, str, str]] = []

    for check in check_configured_model_files(config):
        level = "PASS" if check.ok else "FAIL"
        results.append(
            (
                level,
                f"{check.label} files",
                f"{check.detail} ({check.resolved_source})",
            )
        )

    if skip_load:
        return results

    if any(level == "FAIL" for level, _label, _detail in results):
        results.append(
            (
                "FAIL",
                "model load",
                "skipped because one or more model file checks failed",
            )
        )
        return results

    for label, ok, detail in verify_model_loads(config):
        results.append(("PASS" if ok else "FAIL", label, detail))

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="check files only without loading model objects",
    )
    args = parser.parse_args(argv)

    try:
        results = run_checks(skip_load=args.skip_load)
    except Exception as error:
        print(f"FAIL model readiness config: {error}")
        return 1

    for level, label, detail in results:
        print(f"{level} {label}: {detail}")

    return 1 if any(level == "FAIL" for level, _label, _detail in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
