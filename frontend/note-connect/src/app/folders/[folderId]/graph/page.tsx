import { AppShell } from "@/components/layout/AppShell";
import { ButtonLink } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/StatusState";

type GraphPageProps = {
  params: Promise<{
    folderId: string;
  }>;
};

export default async function GraphPage({ params }: GraphPageProps) {
  const { folderId } = await params;

  return (
    <AppShell>
      <EmptyState
        title="Graph view is planned"
        description="Phase 3 provides the graph access point. Interactive graph visualization is scheduled for Phase 6."
        action={
          <ButtonLink href={`/folders/${encodeURIComponent(folderId)}`}>
            Back to workspace
          </ButtonLink>
        }
      />
    </AppShell>
  );
}
