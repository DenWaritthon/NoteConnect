"use client";

import { useState, type MouseEvent } from "react";
import ReactFlow, {
  BaseEdge,
  EdgeLabelRenderer,
  type Edge,
  type EdgeProps,
  type Node,
} from "reactflow";
import "reactflow/dist/style.css";
import { SlArrowDown } from "react-icons/sl";
import { SlArrowUp } from "react-icons/sl";
import { GrGenai } from "react-icons/gr";

type GraphNote = {
  id: string;
  title: string;
  content: string;
};

type GraphRelation = {
  id: string;
  sourceId: string;
  targetId: string;
  similarityScore: number | null;
  evidence?: unknown;
};

type GraphViewProps = {
  notes: GraphNote[];
  relations: GraphRelation[];
  folderId: string;
};

type RelationEdgeData = {
  folderId: string;
  relationId: string;
  label: string;
  similarityScore: number | null;
  initialEvidence: RelationEvidenceDetail | null;
  curveOffset: number;
  activeRelationId: string | null;
  onActiveRelationChange: (relationId: string | null) => void;
};

type ApiError = Error & {
  status?: number;
};

type RelationEvidenceDetail = {
  relationType: string | null;
  similarityScore: number | null;
  wordOverlap: string | null;
  similarWords: string | null;
};

type GraphNodePosition = {
  x: number;
  y: number;
};

function formatSimilarityScore(score: number | null) {
  if (score === null) {
    return "similarity unavailable";
  }

  return score.toFixed(2);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function getStringField(value: unknown, keys: string[]) {
  if (!isRecord(value)) {
    return null;
  }

  for (const key of keys) {
    const field = value[key];
    if (typeof field === "string" && field.trim()) {
      return field;
    }

    if (typeof field === "number" && Number.isFinite(field)) {
      return String(field);
    }
  }

  return null;
}

function getNumberField(value: unknown, keys: string[]) {
  if (!isRecord(value)) {
    return null;
  }

  for (const key of keys) {
    const field = value[key];
    if (typeof field === "number" && Number.isFinite(field)) {
      return field;
    }

    if (typeof field === "string") {
      const parsed = Number(field);
      if (Number.isFinite(parsed)) {
        return parsed;
      }
    }
  }

  return null;
}

function normalizeFieldName(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]/g, "");
}

function fieldNameMatches(value: string, keys: string[]) {
  const normalizedValue = normalizeFieldName(value);
  return keys.some((key) => normalizeFieldName(key) === normalizedValue);
}

function getNestedFieldValue(value: unknown, keys: string[], depth = 0): unknown {
  if (depth > 5) {
    return null;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const nested = getNestedFieldValue(item, keys, depth + 1);
      if (nested !== null && nested !== undefined) {
        return nested;
      }
    }

    return null;
  }

  if (!isRecord(value)) {
    return null;
  }

  for (const [fieldName, fieldValue] of Object.entries(value)) {
    if (fieldNameMatches(fieldName, keys) && fieldValue !== null && fieldValue !== undefined) {
      return fieldValue;
    }
  }

  const labelledFieldName = getStringField(value, [
    "field",
    "key",
    "label",
    "metric",
    "name",
  ]);
  if (labelledFieldName && fieldNameMatches(labelledFieldName, keys)) {
    for (const valueKey of ["value", "text", "content", "items", "words"]) {
      if (value[valueKey] !== null && value[valueKey] !== undefined) {
        return value[valueKey];
      }
    }
  }

  for (const fieldValue of Object.values(value)) {
    const nested = getNestedFieldValue(fieldValue, keys, depth + 1);
    if (nested !== null && nested !== undefined) {
      return nested;
    }
  }

  return null;
}

function getNestedStringField(value: unknown, keys: string[]) {
  const directValue = getStringField(value, keys);
  if (directValue) {
    return directValue;
  }

  const nestedValue = getNestedFieldValue(value, keys);
  if (typeof nestedValue === "string" && nestedValue.trim()) {
    return nestedValue;
  }

  if (typeof nestedValue === "number" && Number.isFinite(nestedValue)) {
    return String(nestedValue);
  }

  return null;
}

function getNestedNumberField(value: unknown, keys: string[]) {
  const directValue = getNumberField(value, keys);
  if (directValue !== null) {
    return directValue;
  }

  const nestedValue = getNestedFieldValue(value, keys);
  if (typeof nestedValue === "number" && Number.isFinite(nestedValue)) {
    return nestedValue;
  }

  if (typeof nestedValue === "string") {
    const parsed = Number(nestedValue);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }

  return null;
}

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/backend${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });

  const responseText = await response.text();

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`;
    try {
      const body = JSON.parse(responseText);
      message = body.detail ?? body.error ?? message;
    } catch {
      if (responseText) {
        message = responseText;
      }
    }

    const error = new Error(message) as ApiError;
    error.status = response.status;
    throw error;
  }

  if (!responseText) {
    return null as T;
  }

  return JSON.parse(responseText) as T;
}

function unwrapEvidence(value: unknown): unknown {
  if (!isRecord(value)) {
    return value;
  }

  // Support plain evidence objects and common API envelope shapes.
  for (const key of ["evidence", "data", "result"]) {
    if (value[key] !== undefined) {
      return unwrapEvidence(value[key]);
    }
  }

  return value;
}

function formatWordItem(value: unknown): string[] {
  if (typeof value === "string" && value.trim()) {
    return [value];
  }

  if (typeof value === "number" && Number.isFinite(value)) {
    return [String(value)];
  }

  if (Array.isArray(value)) {
    return value.flatMap(formatWordItem);
  }

  if (isRecord(value)) {
    const pair = [
      getStringField(value, ["word1", "word_1", "source_word", "sourceWord"]),
      getStringField(value, ["word2", "word_2", "target_word", "targetWord"]),
    ];
    const pairText =
      pair[0] && pair[1]
        ? `${pair[0]} - ${pair[1]}`
        : getStringField(value, ["word", "text", "token", "term"]);
    const score = getNumberField(value, [
      "score",
      "similarity_score",
      "similarityScore",
    ]);

    if (pairText && score !== null) {
      return [`${pairText} (${score.toFixed(2)})`];
    }

    if (pairText) {
      return [pairText];
    }

    return Object.entries(value).flatMap(([key, item]) => {
      const nestedItems = formatWordItem(item);
      if (nestedItems.length === 0) {
        return [];
      }

      return nestedItems.map((nestedItem) => `${key}: ${nestedItem}`);
    });
  }

  return [];
}

function formatWordOverlap(value: unknown) {
  if (value === null || value === undefined) {
    return null;
  }

  const words = formatWordItem(value);
  return words.length > 0 ? words.join(", ") : "None";
}

function getWordOverlap(value: unknown) {
  for (const key of [
    "words_overlap",
    "wordOverlap",
    "overlap",
    "word_overlap",
    "overlap_words",
    "overlapWords",
    "overlapping_words",
    "overlappingWords",
    "shared_words",
    "sharedWords",
  ]) {
    const fieldValue = isRecord(value) ? value[key] : undefined;
    const formatted = formatWordOverlap(fieldValue ?? getNestedFieldValue(value, [key]));
    if (formatted) {
      return formatted;
    }
  }

  return null;
}

function getSimilarWords(value: unknown) {
  for (const key of [
    "similar_words",
    "similarWords",
    "similar_terms",
    "similarTerms",
    "related_words",
    "relatedWords",
  ]) {
    const fieldValue = isRecord(value) ? value[key] : undefined;
    const formatted = formatWordOverlap(fieldValue ?? getNestedFieldValue(value, [key]));
    if (formatted) {
      return formatted;
    }
  }

  return null;
}

function parseRelationEvidence(value: unknown): RelationEvidenceDetail {
  const evidence = unwrapEvidence(value);

  return {
    relationType: getNestedStringField(evidence, [
      "relation_type",
      "relationType",
      "type",
      "kind",
    ]),
    similarityScore: getNestedNumberField(evidence, [
      "similarity_score",
      "similarityScore",
      "score",
      "similarity",
      "cosine_similarity",
      "cosineSimilarity",
    ]),
    wordOverlap: getWordOverlap(evidence),
    similarWords: getSimilarWords(evidence),
  };
}

async function loadRelationEvidence(folderId: string, relationId: string) {
  const evidence = await apiRequest<unknown>(
    `/folders/${folderId}/relations/${relationId}/evidence`
  );
  return parseRelationEvidence(evidence);
}

function getExplanationText(value: unknown): string | null {
  if (typeof value === "string" && value.trim()) {
    return value;
  }

  if (Array.isArray(value)) {
    for (const item of value) {
      const text = getExplanationText(item);
      if (text) {
        return text;
      }
    }
  }

  if (!isRecord(value)) {
    return null;
  }

  for (const key of [
    "explanation",
    "text",
    "content",
    "summary",
    "reason",
    "rationale",
    "body",
  ]) {
    const text = getExplanationText(value[key]);
    if (text) {
      return text;
    }
  }

  for (const key of ["data", "result"]) {
    const text = getExplanationText(value[key]);
    if (text) {
      return text;
    }
  }

  return null;
}

async function loadRelationExplanation(folderId: string, relationId: string) {
  const path = `/folders/${folderId}/relations/${relationId}/explanation`;

  try {
    const existing = await apiRequest<unknown>(path);
    const existingText = getExplanationText(existing);
    if (existingText) {
      return existingText;
    }
  } catch (err) {
    const status = (err as ApiError).status;
    if (status && status !== 404) {
      throw err;
    }
  }

  const created = await apiRequest<unknown>(path, { method: "POST" });
  return getExplanationText(created) ?? "No explanation text was returned.";
}

function getOffsetCurvePath(
  sourceX: number,
  sourceY: number,
  targetX: number,
  targetY: number,
  curveOffset: number
) {
  const midX = (sourceX + targetX) / 2;
  const midY = (sourceY + targetY) / 2;
  const dx = targetX - sourceX;
  const dy = targetY - sourceY;
  const length = Math.hypot(dx, dy) || 1;
  const offsetDistance = curveOffset * 36;
  const controlX = midX + (-dy / length) * offsetDistance;
  const controlY = midY + (dx / length) * offsetDistance;
  const labelX = midX + (-dy / length) * offsetDistance * 0.55;
  const labelY = midY + (dx / length) * offsetDistance * 0.55;

  return {
    edgePath: `M ${sourceX},${sourceY} Q ${controlX},${controlY} ${targetX},${targetY}`,
    labelX,
    labelY,
  };
}

function getConnectedComponents(notes: GraphNote[], relations: GraphRelation[]) {
  const noteIds = new Set(notes.map((note) => note.id));
  const adjacency = new Map<string, Set<string>>();

  for (const note of notes) {
    adjacency.set(note.id, new Set());
  }

  for (const relation of relations) {
    if (!noteIds.has(relation.sourceId) || !noteIds.has(relation.targetId)) {
      continue;
    }

    adjacency.get(relation.sourceId)?.add(relation.targetId);
    adjacency.get(relation.targetId)?.add(relation.sourceId);
  }

  const visited = new Set<string>();
  const components: string[][] = [];

  for (const note of notes) {
    if (visited.has(note.id)) {
      continue;
    }

    const component: string[] = [];
    const queue = [note.id];
    visited.add(note.id);

    while (queue.length > 0) {
      const current = queue.shift();
      if (!current) {
        continue;
      }

      component.push(current);

      for (const neighbor of adjacency.get(current) ?? []) {
        if (!visited.has(neighbor)) {
          visited.add(neighbor);
          queue.push(neighbor);
        }
      }
    }

    components.push(
      component.sort(
        (left, right) =>
          (adjacency.get(right)?.size ?? 0) - (adjacency.get(left)?.size ?? 0)
      )
    );
  }

  return components.sort((left, right) => right.length - left.length);
}

function getNodePositions(notes: GraphNote[], relations: GraphRelation[]) {
  const positions = new Map<string, GraphNodePosition>();
  const components = getConnectedComponents(notes, relations);
  const groupGapX = 430;
  const groupGapY = 300;
  const columns = Math.max(1, Math.ceil(Math.sqrt(components.length)));

  components.forEach((component, groupIndex) => {
    // Place each connected group in its own area, then orbit related notes.
    const groupColumn = groupIndex % columns;
    const groupRow = Math.floor(groupIndex / columns);
    const centerX = groupColumn * groupGapX;
    const centerY = groupRow * groupGapY;

    if (component.length === 1) {
      positions.set(component[0], { x: centerX, y: centerY });
      return;
    }

    positions.set(component[0], { x: centerX, y: centerY });

    const radius = Math.max(150, Math.min(260, component.length * 46));
    const satellites = component.slice(1);

    satellites.forEach((noteId, satelliteIndex) => {
      const angle =
        (Math.PI * 2 * satelliteIndex) / satellites.length - Math.PI / 2;
      positions.set(noteId, {
        x: centerX + Math.cos(angle) * radius,
        y: centerY + Math.sin(angle) * radius,
      });
    });
  });

  return positions;
}

function RelationEdge({
  sourceX,
  sourceY,
  targetX,
  targetY,
  style,
  markerEnd,
  data,
}: EdgeProps<RelationEdgeData>) {
  const [evidence, setEvidence] = useState<RelationEvidenceDetail | null>(null);
  const [hasLoadedEvidence, setHasLoadedEvidence] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [evidenceLoading, setEvidenceLoading] = useState(false);
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [evidenceError, setEvidenceError] = useState<string | null>(null);
  const [explanationError, setExplanationError] = useState<string | null>(null);
  const isOpen = data?.activeRelationId === data?.relationId;
  const curveOffset = data?.curveOffset ?? 1;
  const { edgePath, labelX, labelY } = getOffsetCurvePath(
    sourceX,
    sourceY,
    targetX,
    targetY,
    curveOffset
  );
  const displayedEvidence = evidence ?? data?.initialEvidence ?? null;
  const hasDetailData = hasLoadedEvidence || data?.initialEvidence != null;

  async function toggleDropdown(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation();
    const nextOpen = !isOpen;
    data?.onActiveRelationChange(nextOpen ? data.relationId : null);

    if (!nextOpen) {
      setShowExplanation(false);
    }

    if (
      !nextOpen ||
      displayedEvidence ||
      evidenceLoading ||
      !data?.folderId
    ) {
      return;
    }

    setEvidenceLoading(true);
    setEvidenceError(null);

    try {
      const nextEvidence = await loadRelationEvidence(
        data.folderId,
        data.relationId
      );
      setEvidence(nextEvidence);
      setHasLoadedEvidence(true);
    } catch (err) {
      setEvidenceError(
        err instanceof Error ? err.message : "Could not load relation detail."
      );
    } finally {
      setEvidenceLoading(false);
    }
  }

  async function toggleExplanation(event: MouseEvent<HTMLButtonElement>) {
    event.stopPropagation();
    const nextOpen = !showExplanation;
    setShowExplanation(nextOpen);

    if (!nextOpen || explanation || explanationLoading || !data?.folderId) {
      return;
    }

    setExplanationLoading(true);
    setExplanationError(null);

    try {
      const nextExplanation = await loadRelationExplanation(
        data.folderId,
        data.relationId
      );
      setExplanation(nextExplanation);
    } catch (err) {
      setExplanationError(
        err instanceof Error ? err.message : "Could not load explanation."
      );
    } finally {
      setExplanationLoading(false);
    }
  }

  return (
    <>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} />
      <EdgeLabelRenderer>
        <div
          className="nodrag nopan absolute"
          style={{
            pointerEvents: "all",
            zIndex: isOpen ? 2147483647 : 1000,
            transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,
          }}
          onClick={(event) => event.stopPropagation()}
        >
          <button
            type="button"
            onClick={toggleDropdown}
            className="inline-flex max-w-[42vw] items-center gap-1 truncate whitespace-nowrap rounded-full border border-blue-200 bg-white px-2.5 py-0.5 text-[10px] font-semibold leading-4 text-gray-800 shadow-sm hover:bg-blue-50 sm:max-w-none"
          >
            <span className="truncate">{data?.label ?? "relation"}</span>
            <span className="shrink-0">
              {isOpen ? <SlArrowUp /> : <SlArrowDown />}
            </span>
          </button>

          {isOpen && (
            <div
              className="absolute bottom-full left-1/2 z-[2147483647] mb-2 w-[min(18rem,78vw)] -translate-x-1/2 rounded-lg border border-gray-200 bg-white p-2.5 text-[11px] leading-4 text-gray-700 shadow-2xl"
              style={{ zIndex: 2147483647 }}
            >
              <div className="mb-2 flex items-center justify-between gap-2 border-b border-gray-100 pb-2">
                <p className="font-semibold text-gray-900">Relation detail</p>
                <button
                  type="button"
                  onClick={toggleExplanation}
                  className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-[10px] font-semibold text-gray-700 hover:bg-gray-100"
                >
                  {showExplanation ? <GrGenai /> : <GrGenai />}
                </button>
              </div>

              {evidenceLoading && <p>Loading detail...</p>}
              {evidenceError && <p className="text-red-600">{evidenceError}</p>}
              {!hasDetailData && !evidenceLoading && !evidenceError && <p>Loading detail...</p>}
              {hasDetailData && !evidenceLoading && !evidenceError && (
                <div className="space-y-1.5">
                  <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
                    <span className="text-gray-500">relation_type</span>
                    <span className="break-words font-medium text-gray-900">
                      {displayedEvidence?.relationType ?? "Unavailable"}
                    </span>
                  </div>
                  <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
                    <span className="text-gray-500">similarity_score</span>
                    <span className="break-words font-medium text-gray-900">
                      {formatSimilarityScore(
                        displayedEvidence?.similarityScore ??
                          data?.similarityScore ??
                          null
                      )}
                    </span>
                  </div>
                  <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
                    <span className="text-gray-500">word_overlap</span>
                    <span className="break-words font-medium text-gray-900">
                      {displayedEvidence?.wordOverlap ?? "Unavailable"}
                    </span>
                  </div>
                  <div className="grid grid-cols-[88px_minmax(0,1fr)] gap-2">
                    <span className="text-gray-500">similar_words</span>
                    <span className="break-words font-medium text-gray-900">
                      {displayedEvidence?.similarWords ?? "Unavailable"}
                    </span>
                  </div>
                </div>
              )}

              {showExplanation && (
                <div className="mt-2 border-t border-gray-100 pt-2">
                  {explanationLoading && <p>Loading explanation...</p>}
                  {explanationError && (
                    <p className="text-red-600">{explanationError}</p>
                  )}
                  {!explanationLoading && !explanationError && (
                    <p className="max-h-28 overflow-y-auto whitespace-pre-wrap">
                      {explanation ?? "No explanation loaded."}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </EdgeLabelRenderer>
    </>
  );
}

const edgeTypes = {
  relation: RelationEdge,
};

export default function GraphView({ notes, relations, folderId }: GraphViewProps) {
  const [activeRelationId, setActiveRelationId] = useState<string | null>(null);
  const noteIds = new Set(notes.map((note) => note.id));
  const drawableRelations = relations.filter(
    (relation) =>
      noteIds.has(relation.sourceId) && noteIds.has(relation.targetId)
  );
  const nodePositions = getNodePositions(notes, drawableRelations);

  const nodes: Node[] = notes.map((note, i) => ({
    id: note.id,
    data: { label: note.title },
    position: nodePositions.get(note.id) ?? {
      x: (i % 3) * 260,
      y: Math.floor(i / 3) * 160,
    },
    style: {
      width: 180,
      maxWidth: 180,
      maxHeight: 84,
      padding: 8,
      borderColor: "#d1d5db",
      borderRadius: 8,
      color: "#1f2937",
      fontSize: 10,
      lineHeight: 1.25,
      overflow: "hidden",
      overflowWrap: "anywhere",
      textOverflow: "ellipsis",
      whiteSpace: "normal",
      wordBreak: "break-word",
    },
  }));

  const curveOffsets = [-3, -2, -1, 1, 2, 3, 4];
  const edges: Edge[] = drawableRelations
    .map((relation, index) => ({
      id: relation.id,
      source: relation.sourceId,
      target: relation.targetId,
      type: "relation",
      data: {
        folderId,
        relationId: relation.id,
        label: formatSimilarityScore(relation.similarityScore),
        similarityScore: relation.similarityScore,
        initialEvidence: relation.evidence
          ? parseRelationEvidence(relation.evidence)
          : null,
        curveOffset: curveOffsets[index % curveOffsets.length],
        activeRelationId,
        onActiveRelationChange: setActiveRelationId,
      },
      animated: true,
      style: { stroke: "#2563eb", strokeWidth: 2.25, opacity: 0.88 },
    }));

  return (
    <div className="relative h-full min-h-[420px]">
      {edges.length === 0 && (
        <div className="absolute inset-x-0 top-0 z-10 bg-amber-50 px-4 py-2 text-xs text-amber-700">
          No drawable relation lines found for these notes.
        </div>
      )}
      <ReactFlow
        className="h-full min-h-[420px] [&_.react-flow__edgelabel-renderer]:!z-[2147483647]"
        nodes={nodes}
        edges={edges}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        onPaneClick={() => setActiveRelationId(null)}
      >
      </ReactFlow>
    </div>
  );
}
