from __future__ import annotations

import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class ExplanationGenerator:
    MODEL_ID = "Qwen/Qwen3-0.6B"

    SYSTEM_PROMPT = (
        "You are a writing assistant. "
        "Given two notes, write a single natural sentence explaining how they relate. "
        "Write as if explaining to a general audience — do not mention scores, labels, "
        "or any technical terms. Focus only on the meaning and topic of the notes. "
        "Output plain text only."
    )

    def __init__(self, max_new_tokens: int = 128) -> None:
        self.max_new_tokens = max_new_tokens
        self._tokenizer: AutoTokenizer | None = None
        self._model: AutoModelForCausalLM | None = None

    def load(self) -> None:
        """Load model and tokenizer into memory. Call once at startup."""
        if self._model is not None:
            return
        print(f"[NLIExplanationGenerator] Loading {self.MODEL_ID} ...")
        self._tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID)
        self._model = AutoModelForCausalLM.from_pretrained(
            self.MODEL_ID,
            torch_dtype=torch.float32,
            device_map="cpu",
            low_cpu_mem_usage=True,
        )
        self._model.eval()
        print("[NLIExplanationGenerator] Model ready.")

    def _ensure_loaded(self) -> None:
        if self._model is None:
            self.load()

    @staticmethod
    def _build_user_prompt(note_1: str, note_2: str) -> str:
        return (
            f"Note 1: {note_1}\n"
            f"Note 2: {note_2}\n\n"
            "How do these two notes relate to each other? "
            "Write one natural sentence."
        )

    @staticmethod
    def _clean_output(raw: str) -> str:
        """Strip noise and unwanted prefixes from model output."""
        first_line = raw.strip().split("\n")[0].strip()
        first_line = re.sub(
            r"^(answer|explanation|result)\s*:\s*",
            "",
            first_line,
            flags=re.IGNORECASE,
        )
        return first_line

    def create_explanation(self, note_1: str, note_2: str) -> str:
        """
        Generate a plain-text explanation of the relationship between two notes.

        Args:
            note_1: First note text.
            note_2: Second note text.

        Returns:
            A single natural sentence describing how the two notes relate.
        """
        self._ensure_loaded()

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user",   "content": self._build_user_prompt(note_1, note_2)},
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

        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        raw = self._tokenizer.decode(new_tokens, skip_special_tokens=True)
        return self._clean_output(raw)