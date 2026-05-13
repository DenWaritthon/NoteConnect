import { AppShell } from "@/components/layout/AppShell";
import { FolderListView } from "@/features/folders/FolderListView";

type FolderPageProps = {
  params: Promise<{
    folderId: string;
  }>;
};

export default async function FolderPage({ params }: FolderPageProps) {
  const { folderId } = await params;

  return (
    <AppShell showSidebar={false}>
      <FolderListView selectedFolderId={folderId} />
    </AppShell>
  );
}
