# Phase 5: Relations & AI Explanation

## Goal

Let users explore relationships between notes with evidence and AI-generated explanations.

## Main Work

- Build `/folders/:folderId/relations`.
- Build `/folders/:folderId/relations/:relationId`.
- Display the relation list.
- Display source and target notes.
- Display similarity scores and relation metadata.
- Load and display evidence.
- Load existing explanations.
- Support explanation generation through the API.
- Display pending, success, and error states for explanation generation.
- Add navigation back to related notes.

## Expected Outcomes

- Users can understand note relationships clearly.
- Users can open relation details to view evidence and explanations.
- The explanation workflow does not duplicate backend logic.
- Relation pages refresh data correctly after generating explanations.

## Out of Scope

- Full graph interaction.
- Relation recomputation in the frontend.
- Advanced filtering unless the backend has supported endpoints.
