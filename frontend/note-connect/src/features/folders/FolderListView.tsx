"use client";

import { useEffect, useMemo, useState } from "react";
import { Button, ButtonLink } from "@/components/ui/Button";
import {
  EmptyState,
  ErrorState,
  LoadingState,
} from "@/components/ui/StatusState";
import {
  createFolder,
  deleteFolder,
  getFolder,
  getFolders,
  getNotes,
  getRelations,
  openFolder,
  updateFolder,
} from "@/services/api";
import { isApiError } from "@/services/api/client";
import type { Folder, Note, Relation } from "@/types/api";

type FolderListViewProps = {
  selectedFolderId?: string;
};

function formatDate(value?: string | null) {
  if (!value) {
    return "Never";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "Unknown";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function getSortTime(folder: Folder) {
  return new Date(folder.last_open_at ?? folder.updated_at ?? 0).getTime();
}

function getErrorMessage(error: unknown) {
  if (isApiError(error)) {
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "The workspace request could not be completed.";
}

export function FolderListView({ selectedFolderId }: FolderListViewProps) {
  const [folders, setFolders] = useState<Folder[]>([]);
  const [folderDetail, setFolderDetail] = useState<Folder | null>(null);
  const [folderStatus, setFolderStatus] = useState<
    "loading" | "success" | "error"
  >("loading");
  const [workspaceStatus, setWorkspaceStatus] = useState<
    "idle" | "loading" | "success" | "error"
  >("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [notes, setNotes] = useState<Note[]>([]);
  const [relations, setRelations] = useState<Relation[]>([]);
  const [currentFolderId, setCurrentFolderId] = useState<string | null>(
    selectedFolderId ?? null,
  );
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [newFolderDescription, setNewFolderDescription] = useState("");
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editFolderId, setEditFolderId] = useState<string | null>(null);
  const [pendingAction, setPendingAction] = useState<string | null>(null);

  const sortedFolders = useMemo(
    () => [...folders].sort((a, b) => getSortTime(b) - getSortTime(a)),
    [folders],
  );
  const activeFolderId = currentFolderId ?? sortedFolders[0]?.folder_id;
  const activeFolder =
    folderDetail?.folder_id === activeFolderId
      ? folderDetail
      : folders.find((folder) => folder.folder_id === activeFolderId) ?? null;
  const isWorkspaceRefreshing =
    Boolean(activeFolder) && workspaceStatus === "loading";
  const hasSyncedEditFields =
    Boolean(activeFolder) && editFolderId === activeFolder?.folder_id;
  const hasFolderChanges = activeFolder && hasSyncedEditFields
    ? editName.trim() !== activeFolder.name ||
      (editDescription.trim() || null) !== (activeFolder.description ?? null)
    : false;

  useEffect(() => {
    const controller = new AbortController();

    void getFolders({ signal: controller.signal })
      .then((nextFolders) => {
        const latestFolder =
          [...nextFolders].sort((a, b) => getSortTime(b) - getSortTime(a))[0] ??
          null;
        const nextFolderId = selectedFolderId ?? latestFolder?.folder_id ?? null;
        const nextFolder =
          nextFolders.find((folder) => folder.folder_id === nextFolderId) ??
          null;

        setFolders(nextFolders);
        setCurrentFolderId((existingFolderId) => existingFolderId ?? nextFolderId);

        if (nextFolder) {
          setEditName(nextFolder.name);
          setEditDescription(nextFolder.description ?? "");
          setEditFolderId(nextFolder.folder_id);
        }

        setFolderDetail((existingDetail) => {
          if (!existingDetail) {
            return existingDetail;
          }

          return (
            nextFolders.find(
              (folder) => folder.folder_id === existingDetail.folder_id,
            ) ?? existingDetail
          );
        });
        setFolderStatus("success");
        setErrorMessage("");
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setFolderStatus("error");
        setErrorMessage(getErrorMessage(error));
      });

    return () => {
      controller.abort();
    };
  }, [selectedFolderId]);

  useEffect(() => {
    if (!activeFolderId) {
      return;
    }

    const controller = new AbortController();
    const fallbackFolder =
      folders.find((folder) => folder.folder_id === activeFolderId) ?? null;

    queueMicrotask(() => {
      if (fallbackFolder) {
        setEditName(fallbackFolder.name);
        setEditDescription(fallbackFolder.description ?? "");
        setEditFolderId(fallbackFolder.folder_id);
      }

      setWorkspaceStatus("loading");
    });

    void Promise.all([
      getFolder(activeFolderId, { signal: controller.signal }),
      getNotes(activeFolderId, { signal: controller.signal }),
      getRelations(activeFolderId, { signal: controller.signal }),
    ])
      .then(([nextFolder, nextNotes, nextRelations]) => {
        setFolderDetail(nextFolder);
        setEditName(nextFolder.name);
        setEditDescription(nextFolder.description ?? "");
        setEditFolderId(nextFolder.folder_id);
        setNotes(nextNotes);
        setRelations(nextRelations);
        setWorkspaceStatus("success");
        setErrorMessage("");
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }

        setWorkspaceStatus("error");
        setErrorMessage(getErrorMessage(error));
      });

    return () => {
      controller.abort();
    };
  }, [activeFolderId, folders]);

  async function refreshFolders() {
    const nextFolders = await getFolders();
    setFolders(nextFolders);
    setFolderStatus("success");
    setErrorMessage("");
    return nextFolders;
  }

  function setWorkspaceUrl(folderId: string | null) {
    if (typeof window === "undefined") {
      return;
    }

    const nextPath = folderId ? `/folders/${encodeURIComponent(folderId)}` : "/folders";

    window.history.pushState(null, "", nextPath);
  }

  function resetCreateForm() {
    setNewFolderName("");
    setNewFolderDescription("");
  }

  function closeCreateDialog() {
    resetCreateForm();
    setShowCreateDialog(false);
  }

  async function handleCreateFolder(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = newFolderName.trim();

    if (!trimmedName) {
      return;
    }

    setPendingAction("create");

    try {
      const folder = await createFolder({
        name: trimmedName,
        description: newFolderDescription.trim() || null,
      });
      await openFolder(folder.folder_id);
      await refreshFolders();
      closeCreateDialog();
      setCurrentFolderId(folder.folder_id);
      setWorkspaceUrl(folder.folder_id);
    } catch (error) {
      setFolderStatus("error");
      setErrorMessage(getErrorMessage(error));
    } finally {
      setPendingAction(null);
    }
  }

  async function handleSelectFolder(folderId: string) {
    const nextFolder = folders.find((folder) => folder.folder_id === folderId);

    if (nextFolder) {
      setEditName(nextFolder.name);
      setEditDescription(nextFolder.description ?? "");
      setEditFolderId(nextFolder.folder_id);
    }

    setCurrentFolderId(folderId);
    setWorkspaceUrl(folderId);
    setPendingAction(`open-${folderId}`);

    try {
      await openFolder(folderId);
      await refreshFolders();
    } catch {
      // Keep navigation responsive even if last-opened metadata fails.
    } finally {
      setPendingAction(null);
    }
  }

  async function handleSaveFolder() {
    if (!activeFolder) {
      return;
    }

    const trimmedName = editName.trim();

    if (!trimmedName) {
      return;
    }

    setPendingAction("save-folder");

    try {
      const nextFolder = await updateFolder(activeFolder.folder_id, {
        name: trimmedName,
        description: editDescription.trim() || null,
      });
      setFolderDetail(nextFolder);
      setEditName(nextFolder.name);
      setEditDescription(nextFolder.description ?? "");
      setEditFolderId(nextFolder.folder_id);
      await refreshFolders();
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
      setWorkspaceStatus("error");
    } finally {
      setPendingAction(null);
    }
  }

  async function handleDeleteFolder() {
    if (!activeFolder) {
      return;
    }

    const confirmed = window.confirm(
      `Delete "${activeFolder.name}" and its workspace data?`,
    );

    if (!confirmed) {
      return;
    }

    setPendingAction("delete-folder");

    try {
      const remainingFolders = await deleteFolder(activeFolder.folder_id).then(
        refreshFolders,
      );
      const nextFolder = [...remainingFolders].sort(
        (a, b) => getSortTime(b) - getSortTime(a),
      )[0];

      setFolderDetail(null);
      setEditFolderId(nextFolder?.folder_id ?? null);
      setCurrentFolderId(nextFolder?.folder_id ?? null);
      setWorkspaceUrl(nextFolder?.folder_id ?? null);
    } catch (error) {
      setErrorMessage(getErrorMessage(error));
      setWorkspaceStatus("error");
    } finally {
      setPendingAction(null);
    }
  }

  return (
    <section>
      <div className="grid gap-6 xl:grid-cols-[20rem_minmax(0,1fr)]">
        <aside className="rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-4">
          <div className="flex items-center justify-between gap-3">
            <h2 className="text-sm font-semibold text-[var(--color-foreground)]">
              Folders
            </h2>
            {sortedFolders.length > 0 ? (
              <Button
                type="button"
                variant="secondary"
                className="min-h-9 px-3"
                onClick={() => setShowCreateDialog(true)}
              >
                New
              </Button>
            ) : null}
          </div>

          {folderStatus === "loading" ? (
            <div className="mt-4">
              <LoadingState
                title="Loading folders"
                description="Fetching your workspaces."
              />
            </div>
          ) : null}

          {folderStatus === "error" ? (
            <div className="mt-4">
              <ErrorState
                title="Folder data unavailable"
                description={errorMessage}
                action={
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={() => void refreshFolders()}
                  >
                    Retry
                  </Button>
                }
              />
            </div>
          ) : null}

          {folderStatus === "success" && sortedFolders.length === 0 ? (
            <div className="mt-4">
              <p className="text-sm text-[var(--color-muted-foreground)]">
                No folders yet. Create a folder to start your workspace.
              </p>
              <Button
                type="button"
                className="mt-4 w-full"
                onClick={() => setShowCreateDialog(true)}
              >
                New folder
              </Button>
            </div>
          ) : null}

          {folderStatus === "success" && sortedFolders.length > 0 ? (
            <div className="mt-4 space-y-2">
              {sortedFolders.map((folder) => {
                const isActive = folder.folder_id === activeFolderId;

                return (
                  <button
                    key={folder.folder_id}
                    type="button"
                    onClick={() => void handleSelectFolder(folder.folder_id)}
                    disabled={pendingAction === `open-${folder.folder_id}`}
                    className={`block w-full rounded-lg border p-3 text-left transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)] ${
                      isActive
                        ? "border-[var(--color-primary)] bg-[var(--color-panel-strong)]"
                        : "border-[var(--color-border)] bg-[var(--color-background)] hover:bg-[var(--color-panel-strong)]"
                    }`}
                  >
                    <span className="block truncate text-sm font-semibold text-[var(--color-foreground)]">
                      {folder.name}
                    </span>
                    <span className="mt-1 block text-xs text-[var(--color-muted-foreground)]">
                      Last opened {formatDate(folder.last_open_at)}
                    </span>
                  </button>
                );
              })}
            </div>
          ) : null}
        </aside>

        <main className="min-w-0">
          {!activeFolder ? (
            <EmptyState
              title="No folder selected"
              description="Create a folder from the left panel to start working."
            />
          ) : null}

          {activeFolder && workspaceStatus === "error" ? (
            <ErrorState
              title="Workspace unavailable"
              description={errorMessage}
            />
          ) : null}

          {activeFolder && workspaceStatus !== "error" ? (
            <section
              aria-busy={isWorkspaceRefreshing}
              className="relative overflow-hidden rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5 shadow-sm transition-[border-color,box-shadow,opacity] duration-300 ease-out"
            >
              <div
                className={`pointer-events-none absolute inset-x-0 top-0 h-0.5 bg-[var(--color-primary)] transition-opacity duration-200 ${
                  isWorkspaceRefreshing ? "opacity-100" : "opacity-0"
                }`}
              />
              <div className="mb-5 flex flex-wrap items-center justify-between gap-3 border-b border-[var(--color-border)] pb-3">
                <div className="flex shrink-0 gap-3 rounded-lg bg-[var(--color-panel-strong)] px-3 py-2">
                  <div>
                    <p className="text-xs text-[var(--color-muted-foreground)]">
                      Notes
                    </p>
                    <p className="text-base font-semibold text-[var(--color-foreground)]">
                      {notes.length}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-[var(--color-muted-foreground)]">
                      Relations
                    </p>
                    <p className="text-base font-semibold text-[var(--color-foreground)]">
                      {relations.length}
                    </p>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button
                    type="button"
                    variant={hasFolderChanges ? "primary" : "secondary"}
                    className="min-h-9 px-3 text-xs disabled:cursor-not-allowed disabled:opacity-55"
                    onClick={() => void handleSaveFolder()}
                  disabled={
                      !hasSyncedEditFields ||
                      !editName.trim() ||
                      !hasFolderChanges ||
                      pendingAction === "save-folder"
                    }
                  >
                    Save
                  </Button>
                  <Button
                    type="button"
                    variant="ghost"
                    className="min-h-9 px-3 text-xs disabled:cursor-not-allowed disabled:opacity-55"
                    onClick={() => void handleDeleteFolder()}
                    disabled={pendingAction === "delete-folder"}
                  >
                    Delete
                  </Button>
                  <ButtonLink
                    href={`/folders/${encodeURIComponent(activeFolder.folder_id)}/graph`}
                    variant="secondary"
                    className="min-h-9 px-3 text-xs"
                  >
                    Open graph
                  </ButtonLink>
                </div>
              </div>

              <div
                className={`space-y-2 transition-opacity duration-200 ease-out ${
                  isWorkspaceRefreshing ? "opacity-70" : "opacity-100"
                }`}
              >
                <input
                  aria-label="Folder name"
                  value={editName}
                  onChange={(event) => setEditName(event.target.value)}
                  className="w-full border-0 bg-transparent p-0 text-3xl font-semibold text-[var(--color-foreground)] outline-none placeholder:text-[var(--color-muted-foreground)]"
                  placeholder="Folder name"
                />
                <textarea
                  aria-label="Folder description"
                  value={editDescription}
                  onChange={(event) => setEditDescription(event.target.value)}
                  rows={1}
                  className="min-h-7 w-full resize-none border-0 bg-transparent p-0 text-sm leading-7 text-[var(--color-muted-foreground)] outline-none [field-sizing:content] placeholder:text-[var(--color-muted-foreground)]"
                  placeholder="Folder description"
                />
              </div>

              <hr className="my-5 border-[var(--color-border)]" />

              <div
                className={`transition-opacity duration-200 ease-out ${
                  isWorkspaceRefreshing ? "opacity-70" : "opacity-100"
                }`}
              >
                {notes.length === 0 ? (
                  <p className="text-sm text-[var(--color-muted-foreground)]">
                    No notes yet. Phase 4 will add note creation and editing for
                    this folder.
                  </p>
                ) : (
                  <div className="space-y-1">
                    {notes.map((note) => (
                      <p
                        key={note.note_id}
                        className="text-sm leading-7 text-[var(--color-foreground)]"
                      >
                        {note.sentence}
                      </p>
                    ))}
                  </div>
                )}
              </div>
            </section>
          ) : null}
        </main>
      </div>

      {showCreateDialog ? (
        <CreateFolderDialog
          name={newFolderName}
          description={newFolderDescription}
          isPending={pendingAction === "create"}
          onNameChange={setNewFolderName}
          onDescriptionChange={setNewFolderDescription}
          onSubmit={handleCreateFolder}
          onClose={closeCreateDialog}
        />
      ) : null}
    </section>
  );
}

type CreateFolderDialogProps = {
  name: string;
  description: string;
  isPending: boolean;
  onNameChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  onSubmit: (event: React.FormEvent<HTMLFormElement>) => void;
  onClose: () => void;
};

function CreateFolderDialog({
  name,
  description,
  isPending,
  onNameChange,
  onDescriptionChange,
  onSubmit,
  onClose,
}: CreateFolderDialogProps) {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="create-folder-title"
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 px-4 py-6"
    >
      <div className="w-full max-w-md rounded-lg border border-[var(--color-border)] bg-[var(--color-panel)] p-5 shadow-xl">
        <div className="flex items-center justify-between gap-3">
          <h2
            id="create-folder-title"
            className="text-lg font-semibold text-[var(--color-foreground)]"
          >
            New folder
          </h2>
          <button
            type="button"
            aria-label="Close new folder dialog"
            onClick={onClose}
            className="inline-flex h-9 w-9 items-center justify-center rounded-full border border-[var(--color-border)] text-lg leading-none text-[var(--color-muted-foreground)] transition hover:bg-[var(--color-panel-strong)] hover:text-[var(--color-foreground)] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-ring)]"
          >
            ×
          </button>
        </div>
        <form onSubmit={onSubmit} className="mt-5 space-y-3">
          <label
            htmlFor="folder-name"
            className="block text-sm font-semibold text-[var(--color-foreground)]"
          >
            Folder name
          </label>
          <input
            id="folder-name"
            value={name}
            onChange={(event) => onNameChange(event.target.value)}
            className="min-h-11 w-full rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] px-3 text-sm text-[var(--color-foreground)] outline-none transition focus:border-[var(--color-ring)]"
            placeholder="Research notes"
          />
          <label
            htmlFor="folder-description"
            className="block text-sm font-semibold text-[var(--color-foreground)]"
          >
            Description
          </label>
          <textarea
            id="folder-description"
            value={description}
            onChange={(event) => onDescriptionChange(event.target.value)}
            className="min-h-24 w-full resize-y rounded-lg border border-[var(--color-border)] bg-[var(--color-background)] px-3 py-2 text-sm text-[var(--color-foreground)] outline-none transition focus:border-[var(--color-ring)]"
            placeholder="Description"
          />
          <Button
            type="submit"
            className="w-full"
            disabled={!name.trim() || isPending}
          >
            {isPending ? "Creating..." : "Create folder"}
          </Button>
        </form>
      </div>
    </div>
  );
}
