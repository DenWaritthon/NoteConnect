"""Text generation for relation explanations."""

from __future__ import annotations

import gc
import logging
import re
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.core.constants import (
    ERROR_EXPLANATION_PAYLOAD_INCOMPLETE,
    LLM_PAYLOAD_NOTE_1,
    LLM_PAYLOAD_NOTE_2,
    LLM_PAYLOAD_QUESTION_PROMPT,
    LLM_PAYLOAD_REQUIRED_KEYS,
    LLM_PAYLOAD_SYSTEM_PROMPT,
)
from src.core.model_readiness import resolve_model_reference
from src.core.timing import Timer


logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """Generate natural-language relation explanations from LLM payloads."""

    REQUIRED_PAYLOAD_KEYS = LLM_PAYLOAD_REQUIRED_KEYS

    def __init__(
        self,
        model_name: str,
        max_new_tokens: int,
        load_mode: str = "startup",
    ) -> None:
        if load_mode not in {"startup", "lazy"}:
            raise ValueError("EXPLANATION_LOAD_MODE must be either 'startup' or 'lazy'.")

        self.model_name = resolve_model_reference(model_name)
        self.max_new_tokens = max_new_tokens
        self.load_mode = load_mode
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForCausalLM | None = None
        self._verified_loadable = False

    def load(self) -> None:
        """Load model and tokenizer once at application startup."""
        if self._model is not None:
            return

        timer = Timer()
        logger.info("Loading explanation model %s", self.model_name)
        self._tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            local_files_only=True,
        )
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
            local_files_only=True,
        )
        self._model.eval()
        self._verified_loadable = True
        logger.info("Explanation model loaded duration_ms=%s", timer.elapsed_ms)

    def unload(self) -> None:
        """Release model references after a lazy generation run."""
        self._model = None
        self._tokenizer = None
        gc.collect()
        logger.info("Explanation model unloaded")

    def model_status(self) -> str:
        """Return whether the explanation model is currently resident in memory."""
        return "loaded" if self._model is not None else "not_loaded"

    def verified_loadable(self) -> bool:
        """Return whether this process has successfully loaded the model before."""
        return self._verified_loadable

    def verify_loadable(self) -> bool:
        """Load once to prove the local model is usable, then unload in lazy mode."""
        if self._verified_loadable:
            return True

        self.load()
        if self.load_mode == "lazy":
            self.unload()
        return self._verified_loadable

    def create_explanation(self, llm_payload: dict[str, Any]) -> str:
        """Generate one explanation using the stored payload as model input."""
        self._validate_payload(llm_payload)

        if self.load_mode == "lazy":
            try:
                # Lazy mode trades latency for memory: load only for this request
                # and release references immediately after generation.
                logger.info("Lazy explanation generation requested")
                self.load()
                return self._generate(llm_payload)
            finally:
                self.unload()

        self._ensure_loaded()
        return self._generate(llm_payload)

    def _generate(self, llm_payload: dict[str, Any]) -> str:
        # The prompt is reconstructed only from llm_payload so old evidence stays
        # reproducible and generation does not depend on mutable note fields.
        messages = [
            {
                "role": "system",
                "content": self._join_prompt(llm_payload[LLM_PAYLOAD_SYSTEM_PROMPT]),
            },
            {
                "role": "user",
                "content": self._build_user_prompt(llm_payload),
            },
        ]
        text = self._tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=False,
        )
        inputs = self._tokenizer(text, return_tensors="pt")

        with torch.no_grad():
            output_ids = self._model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
                temperature=None,
                top_p=None,
                top_k=None,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        new_tokens = output_ids[0][inputs["input_ids"].shape[1] :]
        raw = self._tokenizer.decode(new_tokens, skip_special_tokens=True)
        explanation = self._clean_output(raw)
        if not explanation:
            raise ValueError("Explanation generation returned empty output.")
        return explanation

    def _ensure_loaded(self) -> None:
        if self._model is None:
            self.load()

    def _validate_payload(self, llm_payload: dict[str, Any]) -> None:
        # Older evidence without the required payload shape is rejected rather
        # than guessed from relation/note columns.
        missing_keys = self.REQUIRED_PAYLOAD_KEYS - llm_payload.keys()
        if missing_keys:
            raise ValueError(ERROR_EXPLANATION_PAYLOAD_INCOMPLETE)

        for key in (LLM_PAYLOAD_NOTE_1, LLM_PAYLOAD_NOTE_2):
            if not isinstance(llm_payload[key], str) or not llm_payload[key].strip():
                raise ValueError(ERROR_EXPLANATION_PAYLOAD_INCOMPLETE)

        for key in (LLM_PAYLOAD_SYSTEM_PROMPT, LLM_PAYLOAD_QUESTION_PROMPT):
            if not self._join_prompt(llm_payload[key]).strip():
                raise ValueError(ERROR_EXPLANATION_PAYLOAD_INCOMPLETE)

    def _build_user_prompt(self, llm_payload: dict[str, Any]) -> str:
        question_prompt = self._join_prompt(llm_payload[LLM_PAYLOAD_QUESTION_PROMPT])
        return (
            f"Note 1: {llm_payload[LLM_PAYLOAD_NOTE_1]}\n"
            f"Note 2: {llm_payload[LLM_PAYLOAD_NOTE_2]}\n\n"
            f"{question_prompt}"
        )

    def _join_prompt(self, value: Any) -> str:
        if isinstance(value, list):
            return "".join(str(part) for part in value)
        if isinstance(value, str):
            return value
        raise ValueError(ERROR_EXPLANATION_PAYLOAD_INCOMPLETE)

    def _clean_output(self, raw: str) -> str:
        # Keep the API value as plain text even if the model prefixes its answer.
        first_line = raw.strip().split("\n")[0].strip()
        return re.sub(
            r"^(answer|explanation|result)\s*:\s*",
            "",
            first_line,
            flags=re.IGNORECASE,
        )
