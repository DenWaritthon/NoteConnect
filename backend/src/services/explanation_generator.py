"""Text generation for relation explanations."""

from __future__ import annotations

import re
from typing import Any

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class ExplanationGenerator:
    """Generate natural-language relation explanations from LLM payloads."""

    REQUIRED_PAYLOAD_KEYS = {"note_1", "note_2", "system_prompt", "question_prompt"}

    def __init__(
        self,
        model_name: str,
        max_new_tokens: int,
    ) -> None:
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForCausalLM | None = None

    def load(self) -> None:
        """Load model and tokenizer once at application startup."""
        if self._model is not None:
            return

        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
        )
        self._model.eval()

    def create_explanation(self, llm_payload: dict[str, Any]) -> str:
        """Generate one explanation using the stored payload as model input."""
        self._ensure_loaded()
        self._validate_payload(llm_payload)

        messages = [
            {
                "role": "system",
                "content": self._join_prompt(llm_payload["system_prompt"]),
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
        missing_keys = self.REQUIRED_PAYLOAD_KEYS - llm_payload.keys()
        if missing_keys:
            raise ValueError("Explanation payload is incomplete.")

        for key in ("note_1", "note_2"):
            if not isinstance(llm_payload[key], str) or not llm_payload[key].strip():
                raise ValueError("Explanation payload is incomplete.")

        for key in ("system_prompt", "question_prompt"):
            if not self._join_prompt(llm_payload[key]).strip():
                raise ValueError("Explanation payload is incomplete.")

    def _build_user_prompt(self, llm_payload: dict[str, Any]) -> str:
        question_prompt = self._join_prompt(llm_payload["question_prompt"])
        return (
            f"Note 1: {llm_payload['note_1']}\n"
            f"Note 2: {llm_payload['note_2']}\n\n"
            f"{question_prompt}"
        )

    def _join_prompt(self, value: Any) -> str:
        if isinstance(value, list):
            return "".join(str(part) for part in value)
        if isinstance(value, str):
            return value
        raise ValueError("Explanation payload is incomplete.")

    def _clean_output(self, raw: str) -> str:
        first_line = raw.strip().split("\n")[0].strip()
        return re.sub(
            r"^(answer|explanation|result)\s*:\s*",
            "",
            first_line,
            flags=re.IGNORECASE,
        )
