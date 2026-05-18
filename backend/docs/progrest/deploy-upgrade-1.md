# Deploy Upgrade 1: Offline Model Readiness

Status: Implemented and verified locally after the server issue was reproduced.

## Problem Found After Deploy

During server/local runtime testing, the backend failed during application
startup while loading the embedding model from `backend/model/all-mpnet-base-v2`.
The error was:

```text
safetensors_rust.SafetensorError: Error while deserializing header: header too large
```

The model files existed, but the weight files were only Git LFS pointer stubs
instead of real model weights. Example:

```text
version https://git-lfs.github.com/spec/v1
oid sha256:...
size ...
```

This meant the server could find the model path, but the model was not actually
usable. The backend also needed a clearer pre-start check so this kind of issue
is caught before running uvicorn/nohup.

## What Was Changed

- Added `backend/src/core/model_readiness.py`.
  - Resolves local model paths relative to `backend/`.
  - Detects missing local model directories.
  - Detects missing model weight files.
  - Detects Git LFS pointer weight files.
- Added `backend/scripts/check_model_ready.py`.
  - Checks configured embedding, NLI, and explanation model files.
  - Can load all configured models with local files only.
  - Supports `--skip-load` for a faster file-only check.
- Updated model loading to use local/offline behavior.
  - `SentenceProcessor` resolves local paths before loading embedding/NLI.
  - `ExplanationGenerator` resolves local paths before loading the explanation
    model.
  - Model loaders use `local_files_only=True`.
- Updated `/ready`.
  - Adds `model_verified_loadable`.
  - Adds `embedding_model_status`.
  - Adds `nli_model_status`.
  - Adds `explanation_model_status`.
  - Returns `503 Model is not ready.` if model readiness fails.
- Preserved `EXPLANATION_LOAD_MODE=lazy`.
  - In lazy mode, `/ready` verifies that the explanation model can load, then
    unloads it.
  - `explanation_model_status` is expected to be `not_loaded` after lazy
    readiness verification.
- Updated `.env.example` for local model paths and offline runtime flags.
- Added unit tests for model readiness helper, readiness response behavior, and
  `check_model_ready.py`.

## How To Use The New Check

Run this before starting the server:

```bash
cd backend
.venv/bin/python scripts/check_model_ready.py
```

For a faster file-only check:

```bash
.venv/bin/python scripts/check_model_ready.py --skip-load
```

Expected success:

```text
PASS embedding files: ...
PASS nli files: ...
PASS explanation files: ...
PASS embedding load: loaded
PASS nli load: loaded
PASS explanation load: loaded
```

If a model was cloned without real Git LFS weights, the check fails before the
server starts.

## Result

The backend is safer for internal/nohup deployment:

- model path mistakes are caught before startup
- Git LFS pointer files are detected clearly
- runtime model loading uses local files only
- `/ready` now confirms both DB and model readiness
- lazy explanation mode still avoids holding the explanation model in RAM
- the server can run without relying on internet access after model files are
  prepared

## Verification

Local verification after implementation:

```text
git diff --check: PASS
compileall src main.py scripts/check_model_ready.py: PASS
unit tests: Ran 32 tests, OK
manual model fix with git lfs pull: PASS
server startup after real model weights were available: PASS
```
