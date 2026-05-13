import { AppShell } from "@/components/layout/AppShell";
import { FolderListView } from "@/features/folders/FolderListView";

export default function FoldersPage() {
  return (
    <AppShell showSidebar={false}>
      <FolderListView />
    </AppShell>
  );
}
