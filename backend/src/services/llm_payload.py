"""Build the stored LLM payload used by explanation generation."""

from __future__ import annotations

from src.core.constants import (
    LLM_PAYLOAD_NOTE_1,
    LLM_PAYLOAD_NOTE_2,
    LLM_PAYLOAD_QUESTION_PROMPT,
    LLM_PAYLOAD_SYSTEM_PROMPT,
)


SYSTEM_PROMPT = [
    "You are a writing assistant. ",
    "Given two notes, write a single natural sentence explaining how they relate. ",
    "Write as if explaining to a general audience — do not mention scores, labels, ",
    "or any technical terms. Focus only on the meaning and topic of the notes. ",
    "Output plain text only.",
]

QUESTION_PROMPT = [
    "How do these two notes relate to each other? ",
    "Write one natural sentence.",
]


def build_relation_llm_payload(note_1: str, note_2: str) -> dict[str, object]:
    """Return the AGENTS.md-compatible explanation payload shape."""
    return {
        LLM_PAYLOAD_NOTE_1: note_1,
        LLM_PAYLOAD_NOTE_2: note_2,
        LLM_PAYLOAD_SYSTEM_PROMPT: SYSTEM_PROMPT,
        LLM_PAYLOAD_QUESTION_PROMPT: QUESTION_PROMPT,
    }
