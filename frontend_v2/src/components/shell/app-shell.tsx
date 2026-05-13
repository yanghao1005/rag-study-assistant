import { SidebarNav } from "@/components/shell/sidebar-nav";
import { TopToolbar } from "@/components/shell/top-toolbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[var(--sl-base)] p-2 lg:p-3">
      <div className="mx-auto grid min-h-[calc(100vh-1rem)] w-full max-w-[1700px] grid-cols-1 overflow-hidden rounded-2xl border border-[var(--sl-muted)] bg-white shadow-sl-sm lg:grid-cols-[280px_1fr]">
        <aside className="hidden border-r border-[var(--sl-muted)] bg-white px-4 py-6 lg:block">
          <div className="mb-6 rounded-sl-soft border border-[var(--sl-muted)] bg-[var(--sl-base)] p-4">
            <p className="text-lg font-semibold text-[var(--sl-text-primary)]">RAG Study Assistant</p>
            <p className="mt-1 text-sm text-[var(--sl-text-secondary)]">Subject-first workspace</p>
            <p className="mt-3 text-xs text-[var(--sl-text-secondary)]">Start in Subjects, enter one subject, then use all study features inside that context.</p>
          </div>
          <SidebarNav />
        </aside>
        <div className="flex min-h-screen flex-col bg-[var(--sl-base)]">
          <TopToolbar />
          <main className="page-enter flex-1 px-4 py-6 lg:px-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
