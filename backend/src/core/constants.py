"""Shared constants for stable service contracts and error messages."""

from __future__ import annotations


PROCESS_STATUS_RELATION_CONFIRMED = "relation_confirmed"
PROCESS_STATUS_ADD_EXPLANATION = "add_explanation"

LLM_PAYLOAD_NOTE_1 = "note_1"
LLM_PAYLOAD_NOTE_2 = "note_2"
LLM_PAYLOAD_SYSTEM_PROMPT = "system_prompt"
LLM_PAYLOAD_QUESTION_PROMPT = "question_prompt"
LLM_PAYLOAD_REQUIRED_KEYS = frozenset(
    {
        LLM_PAYLOAD_NOTE_1,
        LLM_PAYLOAD_NOTE_2,
        LLM_PAYLOAD_SYSTEM_PROMPT,
        LLM_PAYLOAD_QUESTION_PROMPT,
    }
)

ERROR_FOLDER_NOT_FOUND = "Folder not found."
ERROR_NOTE_NOT_FOUND = "Note not found."
ERROR_RELATION_EVIDENCE_NOT_FOUND = "Relation evidence not found."
ERROR_EXPLANATION_NOT_FOUND = "Explanation not found."
ERROR_EXPLANATION_PAYLOAD_INCOMPLETE = "Explanation payload is incomplete."
ERROR_SENTENCE_EMPTY = "Sentence must not be empty."
