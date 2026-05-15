"use client";

import { useState, useEffect, useRef } from "react";
import Modal from "@/components/Modal";
import GraphView from "@/components/GraphView";
import {
    Maximize,
    Minimize,
    FolderPlus,
    RefreshCw,
    Trash2,
    Network,
} from "lucide-react";

type Folder = {
    folder_id: string;
    name: string;
    description?: string | null;
    last_open_at?: string | null;
};

type ApiNote = {
    note_id: string;
    folder_id?: string;
    sentence: string;
};

type NoteLine = ApiNote & {
    draftId: string;
};

type GraphRelation = {
    id: string;
    sourceId: string;
    targetId: string;
    similarityScore: number | null;
};

const emptyFolderName = "Untitled Folder";

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
    const response = await fetch(`/api/backend${path}`, {
        ...init,
        headers: {
            "Content-Type": "application/json",
            ...(init?.headers ?? {}),
        },
    });

    if (!response.ok) {
        let message = `Request failed with status ${response.status}`;
        try {
            const body = await response.json();
            message = body.detail ?? message;
        } catch {
            // Keep the status-based message when the API returns non-JSON.
        }
        throw new Error(message);
    }

    return response.json();
}

function splitSentences(content: string) {
    return content
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean);
}

function isRecord(value: unknown): value is Record<string, unknown> {
    return typeof value === "object" && value !== null;
}

function toRecordArray(value: unknown) {
    // The backend may wrap list responses with different keys while it evolves.
    if (Array.isArray(value)) {
        return value.filter(isRecord);
    }

    if (!isRecord(value)) {
        return [];
    }

    for (const key of ["relations", "items", "data", "results"]) {
        const nested = value[key];
        if (Array.isArray(nested)) {
            return nested.filter(isRecord);
        }
    }

    return [];
}

function getStringField(record: Record<string, unknown>, keys: string[]) {
    for (const key of keys) {
        const value = record[key];
        if (typeof value === "string" && value.trim()) {
            return value;
        }

        if (typeof value === "number" && Number.isFinite(value)) {
            return String(value);
        }
    }

    return null;
}

function getNestedStringField(
    record: Record<string, unknown>,
    objectKeys: string[],
    valueKeys: string[]
) {
    for (const objectKey of objectKeys) {
        const value = record[objectKey];
        if (!isRecord(value)) {
            continue;
        }

        const nestedValue = getStringField(value, valueKeys);
        if (nestedValue) {
            return nestedValue;
        }
    }

    return null;
}

function getStringPairField(record: Record<string, unknown>, keys: string[]) {
    // Accept both [id, id] pairs and [{ note_id }, { note_id }] pairs.
    for (const key of keys) {
        const value = record[key];
        if (!Array.isArray(value) || value.length < 2) {
            continue;
        }

        const pair = value
            .map((item) => {
                if (typeof item === "string" && item.trim()) {
                    return item;
                }

                if (typeof item === "number" && Number.isFinite(item)) {
                    return String(item);
                }

                if (isRecord(item)) {
                    return getStringField(item, ["note_id", "noteId", "id", "sentence"]);
                }

                return null;
            })
            .filter((item): item is string => item !== null);

        if (pair.length >= 2) {
            return [pair[0], pair[1]] as const;
        }
    }

    return null;
}

function getNumberField(record: Record<string, unknown>, keys: string[]) {
    for (const key of keys) {
        const value = record[key];
        if (typeof value === "number" && Number.isFinite(value)) {
            return value;
        }

        if (typeof value === "string") {
            const parsed = Number(value);
            if (Number.isFinite(parsed)) {
                return parsed;
            }
        }
    }

    return null;
}

function getSimilarityScore(value: unknown): number | null {
    if (Array.isArray(value)) {
        for (const item of value) {
            const score = getSimilarityScore(item);
            if (score !== null) {
                return score;
            }
        }
    }

    if (!isRecord(value)) {
        return null;
    }

    const directScore = getNumberField(value, [
        "similarity_score",
        "similarityScore",
        "score",
        "similarity",
        "cosine_similarity",
        "cosineSimilarity",
    ]);

    if (directScore !== null) {
        return directScore;
    }

    for (const key of ["evidence", "data", "result"]) {
        const nestedScore = getSimilarityScore(value[key]);
        if (nestedScore !== null) {
            return nestedScore;
        }
    }

    return null;
}

export default function NotesPage() {
    const [folders, setFolders] = useState<Folder[]>([]);
    const [activeFolderId, setActiveFolderId] = useState<string | null>(null);
    const [folderName, setFolderName] = useState(emptyFolderName);
    const [notes, setNotes] = useState<NoteLine[]>([]);
    const [graphRelations, setGraphRelations] = useState<GraphRelation[]>([]);
    const [content, setContent] = useState("");
    const [savedContent, setSavedContent] = useState("");
    const [showGraph, setShowGraph] = useState(false);
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [graphLoading, setGraphLoading] = useState(false);
    const [graphError, setGraphError] = useState<string | null>(null);
    const autosaveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    async function loadFolders(selectFolderId?: string | null) {
        setLoading(true);
        setError(null);

        try {
            const nextFolders = await apiRequest<Folder[]>("/folders");
            setFolders(nextFolders);

            const requestedFolderId =
                selectFolderId === undefined ? activeFolderId : selectFolderId;
            const nextActiveId =
                requestedFolderId &&
                    nextFolders.some((folder) => folder.folder_id === requestedFolderId)
                    ? requestedFolderId
                    : nextFolders[0]?.folder_id ?? null;

            if (nextActiveId) {
                await loadFolder(nextActiveId, nextFolders);
            } else {
                setActiveFolderId(null);
                setFolderName(emptyFolderName);
                setNotes([]);
                setGraphRelations([]);
                setContent("");
                setSavedContent("");
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Could not load folders.");
        } finally {
            setLoading(false);
        }
    }

    async function loadFolder(folderId: string, knownFolders = folders) {
        setError(null);
        setActiveFolderId(folderId);

        const [folder, folderNotes] = await Promise.all([
            apiRequest<Folder>(`/folders/${folderId}`),
            apiRequest<ApiNote[]>(`/folders/${folderId}/notes`),
            apiRequest(`/folders/${folderId}/open`, { method: "PATCH" }),
        ]);

        const nextNotes = folderNotes.map((note) => ({
            ...note,
            draftId: note.note_id,
        }));

        setFolders((current) =>
            current.map((item) =>
                item.folder_id === folder.folder_id ? { ...item, ...folder } : item
            )
        );
        setFolderName(folder.name || knownFolders.find((item) => item.folder_id === folderId)?.name || emptyFolderName);
        setNotes(nextNotes);
        setGraphRelations([]);
        const nextContent = nextNotes.map((note) => note.sentence).join("\n");
        setContent(nextContent);
        setSavedContent(nextContent);
        return nextNotes;
    }

    async function loadRelations(folderId: string, sourceNotes = notes) {
        setGraphLoading(true);
        setGraphError(null);

        try {
            const relationsResponse = await apiRequest<unknown>(`/folders/${folderId}/relations`);
            const relationRows = toRecordArray(relationsResponse);
            // Relations can reference notes by id or sentence, so normalize both.
            const noteIdBySentence = new Map(
                sourceNotes.map((note) => [note.sentence.trim().toLowerCase(), note.note_id])
            );
            const noteIds = new Set(sourceNotes.map((note) => note.note_id));
            const resolveNoteReference = (value: string | null) => {
                if (!value) {
                    return null;
                }

                if (noteIds.has(value)) {
                    return value;
                }

                return noteIdBySentence.get(value.trim().toLowerCase()) ?? null;
            };

            const nextRelations = await Promise.all(
                relationRows.map(async (relation, index) => {
                    const relationId =
                        getStringField(relation, ["relation_id", "relationId", "id"]) ??
                        `relation-${index}`;
                    const relationPair = getStringPairField(relation, [
                        "note_ids",
                        "noteIds",
                        "notes",
                        "note_pair",
                        "notePair",
                        "endpoints",
                    ]);
                    const sourceId = resolveNoteReference(
                        getStringField(relation, [
                            "source_note_id",
                            "sourceNoteId",
                            "source_id",
                            "from_note_id",
                            "fromNoteId",
                            "from_note",
                            "source_note",
                            "source",
                            "from",
                            "note1_id",
                            "noteId1",
                            "note_id_1",
                            "note_1_id",
                            "note1",
                            "note_a_id",
                            "noteAId",
                            "note_id_a",
                            "note_a",
                            "left_note_id",
                            "left",
                        ]) ??
                        getNestedStringField(
                            relation,
                            ["source", "source_note", "from", "note1", "note_a", "left"],
                            ["note_id", "noteId", "id"]
                        ) ??
                        getStringField(relation, [
                            "source_sentence",
                            "sourceSentence",
                            "from_sentence",
                            "source",
                            "from",
                            "note1_sentence",
                            "note_1_sentence",
                            "note1",
                            "left_sentence",
                            "left",
                        ]) ??
                        relationPair?.[0] ??
                        null
                    );
                    const targetId = resolveNoteReference(
                        getStringField(relation, [
                            "target_note_id",
                            "targetNoteId",
                            "target_id",
                            "to_note_id",
                            "toNoteId",
                            "to_note",
                            "target_note",
                            "target",
                            "to",
                            "note2_id",
                            "noteId2",
                            "note_id_2",
                            "note_2_id",
                            "note2",
                            "note_b_id",
                            "noteBId",
                            "note_id_b",
                            "note_b",
                            "right_note_id",
                            "right",
                        ]) ??
                        getNestedStringField(
                            relation,
                            ["target", "target_note", "to", "note2", "note_b", "right"],
                            ["note_id", "noteId", "id"]
                        ) ??
                        getStringField(relation, [
                            "target_sentence",
                            "targetSentence",
                            "to_sentence",
                            "target",
                            "to",
                            "note2_sentence",
                            "note_2_sentence",
                            "note2",
                            "right_sentence",
                            "right",
                        ]) ??
                        relationPair?.[1] ??
                        null
                    );

                    if (!sourceId || !targetId) {
                        return null;
                    }

                    let similarityScore = getSimilarityScore(relation);

                    try {
                        const evidence = await apiRequest<unknown>(
                            `/folders/${folderId}/relations/${relationId}/evidence`
                        );
                        similarityScore = getSimilarityScore(evidence) ?? similarityScore;
                    } catch {
                        // Keep the relation line even if the evidence score is unavailable.
                    }

                    return {
                        id: relationId,
                        sourceId,
                        targetId,
                        similarityScore,
                    };
                })
            );

            setGraphRelations(
                nextRelations.filter((relation): relation is GraphRelation => relation !== null)
            );
        } catch (err) {
            setGraphRelations([]);
            setGraphError(err instanceof Error ? err.message : "Could not load relations.");
        } finally {
            setGraphLoading(false);
        }
    }

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        void loadFolders();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    async function addFolder() {
        setSaving(true);
        setError(null);

        try {
            const folder = await apiRequest<Folder>("/folders", {
                method: "POST",
                body: JSON.stringify({
                    name: "New Folder",
                    description: null,
                }),
            });
            await loadFolders(folder.folder_id);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Could not create folder.");
        } finally {
            setSaving(false);
        }
    }

    async function saveFolderName() {
        if (!activeFolderId) return;

        const nextName = folderName.trim() || emptyFolderName;
        setSaving(true);
        setError(null);

        try {
            const updated = await apiRequest<Folder>(`/folders/${activeFolderId}`, {
                method: "PATCH",
                body: JSON.stringify({ name: nextName }),
            });
            setFolderName(updated.name);
            setFolders((current) =>
                current.map((folder) =>
                    folder.folder_id === activeFolderId
                        ? { ...folder, name: updated.name }
                        : folder
                )
            );
        } catch (err) {
            setError(err instanceof Error ? err.message : "Could not rename folder.");
        } finally {
            setSaving(false);
        }
    }

    async function saveLines() {
        if (!activeFolderId || content === savedContent) return notes;

        const folderId = activeFolderId;
        const nextContent = content;
        const sentences = splitSentences(content);
        setSaving(true);
        setError(null);

        try {
            const max = Math.max(notes.length, sentences.length);
            const nextNotes: NoteLine[] = [];
            let shouldReload = false;

            for (let index = 0; index < max; index += 1) {
                const note = notes[index];
                const sentence = sentences[index];

                if (note && sentence && note.sentence !== sentence) {
                    await apiRequest(`/folders/${folderId}/notes/${note.note_id}`, {
                        method: "PUT",
                        body: JSON.stringify({ sentence }),
                    });
                    nextNotes.push({ ...note, sentence });
                } else if (!note && sentence) {
                    const created = await apiRequest<ApiNote>(`/folders/${folderId}/notes`, {
                        method: "POST",
                        body: JSON.stringify({ sentence }),
                    });
                    if (created?.note_id) {
                        nextNotes.push({ ...created, draftId: created.note_id });
                    } else {
                        shouldReload = true;
                    }
                } else if (note && !sentence) {
                    await apiRequest(`/folders/${folderId}/notes/${note.note_id}`, {
                        method: "DELETE",
                    });
                } else if (note && sentence) {
                    nextNotes.push(note);
                }
            }

            if (shouldReload) {
                return await loadFolder(folderId);
            }

            setNotes(nextNotes);
            setGraphRelations([]);
            setSavedContent(nextContent);
            return nextNotes;
        } catch (err) {
            setError(err instanceof Error ? err.message : "Could not save notes.");
            return null;
        } finally {
            setSaving(false);
        }
    }

    useEffect(() => {
        if (!activeFolderId || content === savedContent) {
            return;
        }

        // Debounce autosave so each pause in typing updates the backend once.
        if (autosaveTimerRef.current) {
            clearTimeout(autosaveTimerRef.current);
        }

        autosaveTimerRef.current = setTimeout(() => {
            void saveLines();
        }, 900);

        return () => {
            if (autosaveTimerRef.current) {
                clearTimeout(autosaveTimerRef.current);
            }
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [activeFolderId, content, savedContent]);

    async function deleteFolder() {
        if (!activeFolderId) return;

        setSaving(true);
        setError(null);

        try {
            await apiRequest(`/folders/${activeFolderId}`, { method: "DELETE" });
            setActiveFolderId(null);
            await loadFolders(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Could not delete folder.");
        } finally {
            setSaving(false);
        }
    }

    async function openGraph() {
        if (!activeFolderId) return;

        const latestNotes = content === savedContent ? notes : await saveLines();
        if (!latestNotes) {
            return;
        }

        setShowGraph(true);
        await loadRelations(activeFolderId, latestNotes);
    }

    const graphNotes = notes.map((note) => ({
        id: note.note_id,
        title: note.sentence || note.note_id,
        content: note.sentence,
    }));

    return (
        <div className="flex min-h-[calc(100svh-5rem)] flex-col gap-3 bg-softBg p-3 sm:gap-4 sm:p-4 md:h-[calc(100svh-5rem)] md:flex-row md:overflow-hidden">

            {/* SIDEBAR */}
            {!isFullscreen && (
                <aside className="flex max-h-[34svh] min-h-0 w-full flex-col rounded-2xl bg-white p-4 shadow-soft md:h-full md:max-h-none md:w-72 md:shrink-0">

                    {/* Header */}
                    <div className="mb-4 flex items-center justify-between gap-3">
                        <h2 className="text-lg font-semibold">Folders</h2>
                        <button
                            onClick={addFolder}
                            disabled={saving}
                            title="Create folder"
                            className="shrink-0 rounded-lg bg-primary p-2 text-white disabled:opacity-50"
                        >
                            <FolderPlus size={18} />
                        </button>
                    </div>

                    {/* Notes List */}
                    <div className="flex min-h-0 flex-1 gap-3 overflow-x-auto pb-1 md:flex-col md:overflow-x-hidden md:overflow-y-auto md:pb-0">
                        {folders.map((folder) => (
                            <div
                                key={folder.folder_id}
                                onClick={() => loadFolder(folder.folder_id)}
                                className={`min-w-36 max-w-52 shrink-0 cursor-pointer rounded-xl p-3 text-sm leading-snug md:min-w-0 md:max-w-none md:shrink ${folder.folder_id === activeFolderId
                                        ? "bg-primary text-white"
                                        : "bg-gray-100"
                                    }`}
                            >
                                {folder.name}
                            </div>
                        ))}
                    </div>
                </aside>
            )}

            {/* EDITOR */}
            <section className="flex min-h-[60svh] flex-1 flex-col rounded-2xl bg-white p-4 shadow-soft sm:p-6 md:h-full md:min-h-0">

                {loading ? (
                    <div className="h-full grid place-items-center text-gray-500">
                        Loading folders...
                    </div>
                ) : activeFolderId ? (
                    <>
                        {/* TOP BAR */}
                        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                            <input
                                className="min-w-0 flex-1 text-2xl font-bold leading-tight outline-none sm:text-3xl"
                                value={folderName}
                                onChange={(e) => setFolderName(e.target.value)}
                                onBlur={saveFolderName}
                            />

                            <div className="flex shrink-0 gap-2">
                                <button
                                    onClick={() => loadFolder(activeFolderId)}
                                    disabled={saving}
                                    title="Refresh"
                                    className="rounded-xl bg-gray-100 p-2 transition hover:bg-gray-200 disabled:opacity-50"
                                >
                                    <RefreshCw size={18} />
                                </button>

                                <button
                                    onClick={() => setIsFullscreen(!isFullscreen)}
                                    title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
                                    className="rounded-xl bg-gray-100 p-2 transition hover:bg-gray-200"
                                >
                                    {isFullscreen ? (
                                        <Minimize size={18} />
                                    ) : (
                                        <Maximize size={18} />
                                    )}
                                </button>
                            </div>
                        </div>

                        {/* CONTENT */}
                        <textarea
                            className="min-h-[48svh] w-full flex-1 resize-none overflow-y-auto text-base leading-7 text-gray-600 outline-none md:min-h-0"
                            placeholder="Write one sentence per line. Each saved line becomes one API note."
                            value={content}
                            onChange={(e) => setContent(e.target.value)}
                            onBlur={() => void saveLines()}
                            onKeyUp={(event) => {
                                if (event.key === "Enter") {
                                    void saveLines();
                                }
                            }}
                        />

                        {error && (
                            <div className="mt-3 rounded-xl bg-red-50 px-4 py-2 text-sm text-red-600">
                                {error}
                            </div>
                        )}

                        {/* ACTION BUTTONS */}
                        <div className="mt-4 flex flex-wrap items-center justify-end gap-2">
                            {saving && (
                                <span className="mr-auto text-xs font-medium text-gray-400">
                                    Saving...
                                </span>
                            )}

                            <button
                                onClick={deleteFolder}
                                disabled={saving}
                                title="Delete folder"
                                className="rounded-xl bg-red-500 px-4 py-2 text-white disabled:opacity-50"
                            >
                                <Trash2 size={18} />
                            </button>

                            <button
                                onClick={openGraph}
                                className="inline-flex min-w-28 items-center justify-center gap-2 rounded-xl bg-primary px-4 py-2 text-white"
                            >
                                <Network size={18} />
                                Relation
                            </button>
                        </div>
                    </>
                ) : (
                    <div className="h-full grid place-items-center text-center text-gray-500">
                        <div>
                            <p className="font-medium">No folder selected</p>
                            <button
                                onClick={addFolder}
                                disabled={saving}
                                className="mt-3 rounded-xl bg-primary px-4 py-2 text-white disabled:opacity-50"
                            >
                                Create folder
                            </button>
                            {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
                        </div>
                    </div>
                )}
            </section>

            {/* GRAPH MODAL */}
            <Modal isOpen={showGraph} onClose={() => setShowGraph(false)}>
                <div className="relative h-full min-h-[420px]">
                    {graphLoading && (
                        <div className="absolute inset-x-0 top-0 z-10 bg-white/90 px-4 py-2 text-sm text-gray-600">
                            Loading relations...
                        </div>
                    )}
                    {graphError && (
                        <div className="absolute inset-x-0 top-0 z-10 bg-red-50 px-4 py-2 text-sm text-red-600">
                            {graphError}
                        </div>
                    )}
                    <GraphView
                        notes={graphNotes}
                        relations={graphRelations}
                        folderId={activeFolderId ?? ""}
                    />
                </div>
            </Modal>
        </div>
    );
}
