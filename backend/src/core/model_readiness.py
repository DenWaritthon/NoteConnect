"""Model path and file checks for offline runtime readiness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.core.config import BACKEND_DIR, AppConfig


GIT_LFS_POINTER_PREFIX = b"version https://git-lfs.github.com/spec/v1"
WEIGHT_FILE_PATTERNS = ("*.safetensors", "*.bin")


@dataclass(frozen=True)
class ModelFileCheck:
    """Result of checking one configured model reference."""

    label: str
    source: str
    resolved_source: str
    ok: bool
    detail: str


def resolve_model_reference(model_reference: str) -> str:
    """Resolve local model paths relative to backend while leaving hub IDs intact."""
    reference_path = Path(model_reference).expanduser()
    if reference_path.is_absolute():
        return str(reference_path)

    backend_path = BACKEND_DIR / reference_path
    if _looks_like_local_path(model_reference) or backend_path.exists():
        return str(backend_path.resolve())

    return model_reference


def check_configured_model_files(config: AppConfig) -> list[ModelFileCheck]:
    """Check local model directories before expensive model loading starts."""
    return [
        check_model_files("embedding", config.embedding_model),
        check_model_files("nli", config.nli_model),
        check_model_files("explanation", config.explanation_model),
    ]


def check_model_files(label: str, model_reference: str) -> ModelFileCheck:
    """Validate local model files and skip file checks for hub-style model IDs."""
    resolved_reference = resolve_model_reference(model_reference)
    resolved_path = Path(resolved_reference)

    if not _looks_like_local_path(model_reference) and not resolved_path.exists():
        return ModelFileCheck(
            label=label,
            source=model_reference,
            resolved_source=resolved_reference,
            ok=True,
            detail="hub model id; file check skipped",
        )

    if not resolved_path.exists():
        return ModelFileCheck(
            label=label,
            source=model_reference,
            resolved_source=resolved_reference,
            ok=False,
            detail="model path does not exist",
        )

    if not resolved_path.is_dir():
        return ModelFileCheck(
            label=label,
            source=model_reference,
            resolved_source=resolved_reference,
            ok=False,
            detail="model path is not a directory",
        )

    weight_files = _find_weight_files(resolved_path)
    if not weight_files:
        return ModelFileCheck(
            label=label,
            source=model_reference,
            resolved_source=resolved_reference,
            ok=False,
            detail="no model weight files found",
        )

    pointer_files = [path for path in weight_files if is_git_lfs_pointer(path)]
    if pointer_files:
        relative = pointer_files[0].relative_to(resolved_path)
        return ModelFileCheck(
            label=label,
            source=model_reference,
            resolved_source=resolved_reference,
            ok=False,
            detail=f"Git LFS pointer found: {relative}",
        )

    return ModelFileCheck(
        label=label,
        source=model_reference,
        resolved_source=resolved_reference,
        ok=True,
        detail=f"{len(weight_files)} weight file(s) available",
    )


def is_git_lfs_pointer(path: Path) -> bool:
    """Return true when a model weight is only a Git LFS pointer stub."""
    try:
        with path.open("rb") as file:
            header = file.read(128)
    except OSError:
        return False

    return header.startswith(GIT_LFS_POINTER_PREFIX)


def _find_weight_files(model_path: Path) -> list[Path]:
    weight_files: list[Path] = []
    for pattern in WEIGHT_FILE_PATTERNS:
        weight_files.extend(model_path.rglob(pattern))
    return sorted(weight_files)


def _looks_like_local_path(model_reference: str) -> bool:
    return model_reference.startswith((".", "/", "~"))
