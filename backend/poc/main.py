from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from NoteStore import NoteStore
from SentenceProcessor import NLIResult, SentenceProcessor


@dataclass(frozen=True)
class NoteSimilarity:
    note_id_1: int
    note_id_2: int
    similarity_score: float


@dataclass
class NoteRelationship:
    note_id_1: int
    note_id_2: int
    similarity_score: float
    relation_label: str
    nli_label: str
    nli_raw_scores: list[float]
    nli_probabilities: list[float]
    word_overlap: Optional[list[str]] = None
    similar_words: Optional[list[dict]] = None


def calculate_neutral_threshold(
    similarity_threshold: float,
    threshold_scale: float,
) -> float:
    """
    Make neutral stricter than the base similarity threshold.

    Example:
        similarity_threshold = 0.30
        threshold_scale = 0.40
        neutral_threshold = 0.30 + (1.0 - 0.30) * 0.40 = 0.58
    """
    return similarity_threshold + (1.0 - similarity_threshold) * threshold_scale


def classify_relation_mode_5(
    sim_score: float,
    nli_label: str,
    similarity_threshold: float,
    threshold_scale: float,
) -> Optional[str]:
    """
    Mode 5 relation logic:
    - similarity is a recall filter
    - NLI classifies logical relation
    - neutral uses a stricter similarity threshold
    """
    abs_sim_score = abs(sim_score)

    if abs_sim_score < similarity_threshold:
        return None

    if nli_label == "entailment":
        return "related_confirmed"

    if nli_label == "contradiction":
        return "related_conflict"

    if nli_label == "neutral":
        neutral_threshold = calculate_neutral_threshold(
            similarity_threshold=similarity_threshold,
            threshold_scale=threshold_scale,
        )
        if abs_sim_score >= neutral_threshold:
            return "related_semantic"
        return None

    return None


def mode_1_add_new_sentence(note_store: NoteStore) -> None:
    note_id = note_store.get_next_note_id()
    note = input("Enter note: ").strip()

    if not note:
        print("Empty note. Nothing saved.")
        return

    note_store.save_note(note_id, note)
    print(f"Note saved ID: {note_id} - {note}")


def mode_7_show_saved_sentences(note_store: NoteStore) -> None:
    if note_store.get_saved_notes_count() == 0:
        print("No saved notes yet.")
        return

    print("Saved notes:")
    for note_id, note in note_store.get_saved_notes():
        print(f"ID: {note_id} - Note: {note}")


def mode_2_calculate_similarity(
    note_store: NoteStore,
    note_processor: SentenceProcessor,
    note_pair_similarity: list[NoteSimilarity],
    calculated_note_pairs: set[tuple[int, int]],
) -> None:
    if note_store.get_saved_notes_count() < 2:
        print("At least 2 notes are required to calculate similarity.")
        return

    saved_notes = note_store.get_saved_notes()

    for i in range(len(saved_notes)):
        for j in range(i + 1, len(saved_notes)):
            note_id_1, _ = saved_notes[i]
            note_id_2, _ = saved_notes[j]
            note_pair = (note_id_1, note_id_2)

            if note_pair in calculated_note_pairs:
                continue

            vector_1 = note_store.get_note_vector(note_id_1)
            vector_2 = note_store.get_note_vector(note_id_2)

            if vector_1 is None or vector_2 is None:
                print(f"Cannot find vectors for pair {note_pair}. Skipping.")
                continue

            similarity_score = note_processor.similarity(vector_1, vector_2)

            note_pair_similarity.append(
                NoteSimilarity(
                    note_id_1=note_id_1,
                    note_id_2=note_id_2,
                    similarity_score=similarity_score,
                )
            )
            calculated_note_pairs.add(note_pair)

            print(
                f"Similarity between Note ID {note_id_1} and Note ID {note_id_2}: "
                f"{similarity_score}"
            )




def mode_3_find_note_relationships(
    note_store: NoteStore,
    note_processor: SentenceProcessor,
    note_pair_similarity: list[NoteSimilarity],
    note_relationships: list[NoteRelationship],
    checked_relationship_pairs: set[tuple[int, int]],
    similarity_threshold: float,
    threshold_scale: float,
) -> None:
    if not note_pair_similarity:
        print("No similarity scores calculated yet.")
        return

    neutral_threshold = calculate_neutral_threshold(
        similarity_threshold=similarity_threshold,
        threshold_scale=threshold_scale,
    )

    print(
        "Find note relationships\n"
        f"- base similarity threshold: {similarity_threshold}\n"
        f"- neutral similarity threshold: {neutral_threshold}"
    )

    for similarity in note_pair_similarity:
        note_pair = (similarity.note_id_1, similarity.note_id_2)

        if note_pair in checked_relationship_pairs:
            continue

        checked_relationship_pairs.add(note_pair)

        if similarity.similarity_score < similarity_threshold:
            print(
                f"Note ID {similarity.note_id_1} - Note ID {similarity.note_id_2}: "
                f"Similarity Score = {similarity.similarity_score} < {similarity_threshold} "
                "→ reject"
            )
            continue

        sentence1 = note_store.get_saved_note_by_id(similarity.note_id_1)
        sentence2 = note_store.get_saved_note_by_id(similarity.note_id_2)

        if sentence1 is None or sentence2 is None:
            print(f"Cannot find notes for pair {note_pair}. Skipping.")
            continue

        nli_result: NLIResult = note_processor.nli_similarity(sentence1, sentence2)

        relation_label = classify_relation_mode_5(
            sim_score=similarity.similarity_score,
            nli_label=nli_result.label,
            similarity_threshold=similarity_threshold,
            threshold_scale=threshold_scale,
        )

        if relation_label is None:
            print(
                f"Note ID {similarity.note_id_1} - Note ID {similarity.note_id_2}: "
                f"Similarity Score = {similarity.similarity_score}, "
                f"NLI Label = {nli_result.label}, "
                f"NLI Raw Scores = {nli_result.raw_scores}, "
                f"Neutral Margin = {nli_result.neutral_margin} "
                "→ reject"
            )
            continue

        relationship = NoteRelationship(
            note_id_1=similarity.note_id_1,
            note_id_2=similarity.note_id_2,
            similarity_score=similarity.similarity_score,
            relation_label=relation_label,
            nli_label=nli_result.label,
            nli_raw_scores=nli_result.raw_scores,
            nli_probabilities=nli_result.probabilities,
        )
        note_relationships.append(relationship)

        print(
            f"Note ID {relationship.note_id_1} - Note ID {relationship.note_id_2}: "
            f"Similarity Score = {relationship.similarity_score}, "
            f"NLI Label = {relationship.nli_label}, "
            f"Relation = {relationship.relation_label}, "
            f"NLI Raw Scores = {relationship.nli_raw_scores}, "
            f"NLI Probabilities = {relationship.nli_probabilities}"
        )


def mode_8_show_note_relationships(note_relationships: list[NoteRelationship]) -> None:
    if not note_relationships:
        print("No note relationships found yet.")
        return

    print("Note relationships:")
    for relationship in note_relationships:
        print(
            f"Note ID {relationship.note_id_1} - Note ID {relationship.note_id_2}: "
            f"Similarity Score = {relationship.similarity_score}, "
            f"NLI Label = {relationship.nli_label}, "
            f"Relation = {relationship.relation_label}, "
            f"Word Overlap = {relationship.word_overlap}, "
            f"Similar Words = {relationship.similar_words}"
        )


def mode_4_find_relationships_overlap(
    note_processor: SentenceProcessor,
    note_store: NoteStore,
    note_relationships: list[NoteRelationship],
    checked_find_overlap_pairs: set[tuple[int, int]]
) -> None:
    if not note_relationships:
        print("No note relationships found yet.")
        return

    print("Finding relationships overlap based on word overlap:")

    for relationship in note_relationships:

        if (relationship.note_id_1, relationship.note_id_2) in checked_find_overlap_pairs:
            continue

        checked_find_overlap_pairs.add((relationship.note_id_1, relationship.note_id_2))
        
        sentence1 = note_store.get_saved_note_by_id(relationship.note_id_1)
        sentence2 = note_store.get_saved_note_by_id(relationship.note_id_2)

        if sentence1 is None or sentence2 is None:
            print(
                f"Cannot find notes for relationship between Note ID {relationship.note_id_1} "
                f"and Note ID {relationship.note_id_2}. Skipping."
            )
            continue

        word_overlap = note_processor.word_overlap(sentence1, sentence2)
        similar_words = note_processor.similar_words(sentence1, sentence2)
        relationship.word_overlap = word_overlap
        relationship.similar_words = similar_words

        print(
            f"Note ID {relationship.note_id_1} - Note ID {relationship.note_id_2}: "
            f"Relation = {relationship.relation_label}, "
            f"NLI Label = {relationship.nli_label}, "
            f"Word Overlap = {word_overlap}, "
            f"Similar Words = {similar_words}"

        )
    

# ---- Inserted helper and mode functions ----
def _remove_pair_from_checked_sets(
    note_id: int,
    calculated_note_pairs: set[tuple[int, int]],
    checked_relationship_pairs: set[tuple[int, int]],
    checked_find_overlap_pairs: set[tuple[int, int]],
) -> None:
    calculated_note_pairs.difference_update(
        {pair for pair in calculated_note_pairs if note_id in pair}
    )
    checked_relationship_pairs.difference_update(
        {pair for pair in checked_relationship_pairs if note_id in pair}
    )
    checked_find_overlap_pairs.difference_update(
        {pair for pair in checked_find_overlap_pairs if note_id in pair}
    )


def _remove_note_results(
    note_id: int,
    note_pair_similarity: list[NoteSimilarity],
    note_relationships: list[NoteRelationship],
) -> None:
    note_pair_similarity[:] = [
        similarity
        for similarity in note_pair_similarity
        if note_id not in (similarity.note_id_1, similarity.note_id_2)
    ]
    note_relationships[:] = [
        relationship
        for relationship in note_relationships
        if note_id not in (relationship.note_id_1, relationship.note_id_2)
    ]


def mode_5_edit_saved_sentence(
    note_store: NoteStore,
    note_pair_similarity: list[NoteSimilarity],
    note_relationships: list[NoteRelationship],
    calculated_note_pairs: set[tuple[int, int]],
    checked_relationship_pairs: set[tuple[int, int]],
    checked_find_overlap_pairs: set[tuple[int, int]],
) -> None:
    if note_store.get_saved_notes_count() == 0:
        print("No saved notes yet.")
        return

    note_id_input = input("Enter note ID to edit: ").strip()
    if not note_id_input.isdigit():
        print("Invalid note ID.")
        return

    note_id = int(note_id_input)
    current_note = note_store.get_saved_note_by_id(note_id)
    if current_note is None:
        print(f"Note ID {note_id} not found.")
        return

    print(f"Current note: {current_note}")
    new_note = input("Enter new note: ").strip()
    if not new_note:
        print("Empty note. Nothing updated.")
        return

    if not note_store.update_note(note_id, new_note):
        print(f"Failed to update Note ID {note_id}.")
        return
    _remove_note_results(
        note_id=note_id,
        note_pair_similarity=note_pair_similarity,
        note_relationships=note_relationships,
    )
    _remove_pair_from_checked_sets(
        note_id=note_id,
        calculated_note_pairs=calculated_note_pairs,
        checked_relationship_pairs=checked_relationship_pairs,
        checked_find_overlap_pairs=checked_find_overlap_pairs,
    )

    print(f"Note ID {note_id} updated: {new_note}")
    print("Related similarity and relationship results were cleared for this note.")


def mode_6_delete_saved_sentence(
    note_store: NoteStore,
    note_pair_similarity: list[NoteSimilarity],
    note_relationships: list[NoteRelationship],
    calculated_note_pairs: set[tuple[int, int]],
    checked_relationship_pairs: set[tuple[int, int]],
    checked_find_overlap_pairs: set[tuple[int, int]],
) -> None:
    if note_store.get_saved_notes_count() == 0:
        print("No saved notes yet.")
        return

    note_id_input = input("Enter note ID to delete: ").strip()
    if not note_id_input.isdigit():
        print("Invalid note ID.")
        return

    note_id = int(note_id_input)
    current_note = note_store.get_saved_note_by_id(note_id)
    if current_note is None:
        print(f"Note ID {note_id} not found.")
        return

    confirm = input(f"Delete Note ID {note_id}: {current_note}? (y/N): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        return

    if not note_store.delete_note(note_id):
        print(f"Failed to delete Note ID {note_id}.")
        return

    _remove_note_results(
        note_id=note_id,
        note_pair_similarity=note_pair_similarity,
        note_relationships=note_relationships,
    )
    _remove_pair_from_checked_sets(
        note_id=note_id,
        calculated_note_pairs=calculated_note_pairs,
        checked_relationship_pairs=checked_relationship_pairs,
        checked_find_overlap_pairs=checked_find_overlap_pairs,
    )

    print(f"Note ID {note_id} deleted.")
    print("Related similarity and relationship results were cleared for this note.")

def mode_9_use_demo_sentences(note_store: NoteStore) -> None:
    demo_sentences = [
        "The cat is on the table.",
        "A cat is sitting on the table.",
        "The dog is in the garden.",
        "There is a dog in the garden.",
        "My car is parked outside.",
        "My car is parked in the garage.",
        "The weather is sunny today.",
        "Now is raining outside.",
        "I buy a new umbrella because of the rain.",
        "I love eating pizza.",
    ]

    start_id = note_store.get_next_note_id()
    for offset, sentence in enumerate(demo_sentences):
        note_id = start_id + offset
        note_store.save_note(note_id, sentence)
        print(f"Demo Note saved ID: {note_id} - {sentence}")


def print_menu() -> None:
    print(
        "mode : \n"
        "    0 : quit\n"
        "    1 : add new sentence\n"
        "    2 : calculate similarity\n"
        "    3 : find note relationships\n"
        "    4 : find relationships overlap\n"
        "    5 : edit save sentence\n"
        "    6 : delete save sentence\n"
        "    7 : show saved sentences\n"
        "    8 : show note relationships\n"
        "    9 : use demo sentences\n"
    )


def main() -> None:
    note_processor = SentenceProcessor()
    note_store = NoteStore(note_processor)

    note_pair_similarity: list[NoteSimilarity] = []
    calculated_note_pairs: set[tuple[int, int]] = set()

    note_relationships: list[NoteRelationship] = []
    checked_relationship_pairs: set[tuple[int, int]] = set()
    checked_find_overlap_pairs: set[tuple[int, int]] = set()

    similarity_threshold = 0.40
    threshold_scale = 0.20

    while True:
        print_menu()
        mode = input("Enter mode: ").strip()

        if mode == "0":
            print("Exiting...")
            break

        if mode == "1":
            mode_1_add_new_sentence(note_store)
        elif mode == "2":
            mode_2_calculate_similarity(
                note_store=note_store,
                note_processor=note_processor,
                note_pair_similarity=note_pair_similarity,
                calculated_note_pairs=calculated_note_pairs,
            )
        elif mode == "3":
            mode_3_find_note_relationships(
                note_store=note_store,
                note_processor=note_processor,
                note_pair_similarity=note_pair_similarity,
                note_relationships=note_relationships,
                checked_relationship_pairs=checked_relationship_pairs,
                similarity_threshold=similarity_threshold,
                threshold_scale=threshold_scale,
            )
        elif mode == "4":
            mode_4_find_relationships_overlap(
                note_processor=note_processor,
                note_store=note_store,
                note_relationships=note_relationships,
                checked_find_overlap_pairs=checked_find_overlap_pairs,
            )
        elif mode == "5":
            mode_5_edit_saved_sentence(
                note_store=note_store,
                note_pair_similarity=note_pair_similarity,
                note_relationships=note_relationships,
                calculated_note_pairs=calculated_note_pairs,
                checked_relationship_pairs=checked_relationship_pairs,
                checked_find_overlap_pairs=checked_find_overlap_pairs,
            )
        elif mode == "6":
            mode_6_delete_saved_sentence(
                note_store=note_store,
                note_pair_similarity=note_pair_similarity,
                note_relationships=note_relationships,
                calculated_note_pairs=calculated_note_pairs,
                checked_relationship_pairs=checked_relationship_pairs,
                checked_find_overlap_pairs=checked_find_overlap_pairs,
            )
        elif mode == "7":
            mode_7_show_saved_sentences(note_store)
        elif mode == "8":
            mode_8_show_note_relationships(note_relationships)
        elif mode == "9":
            mode_9_use_demo_sentences(note_store)
        else:
            print("Invalid mode. Please try again.")


if __name__ == "__main__":
    main()
