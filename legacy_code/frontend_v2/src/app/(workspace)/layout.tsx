import { WorkspaceGuard } from "@/components/auth/workspace-guard";
import { AppShell } from "@/components/shell/app-shell";

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <WorkspaceGuard>
      <AppShell>{children}</AppShell>
    </WorkspaceGuard>
  );
}

