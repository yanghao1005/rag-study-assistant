import { SidebarNav } from "@/components/shell/sidebar-nav";
import { TopToolbar } from "@/components/shell/top-toolbar";

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen px-2 py-2 lg:px-3">
      <div className="mx-auto grid min-h-[calc(100vh-1rem)] w-full max-w-[1700px] grid-cols-1 overflow-hidden rounded-2xl border bg-card/40 shadow-sm lg:grid-cols-[290px_1fr]">
        <aside className="hidden border-r bg-sidebar/85 px-4 py-6 backdrop-blur lg:block">
          <div className="mb-6 rounded-2xl border bg-background/70 p-4">
            <p className="font-heading text-lg font-semibold">RAG Study Assistant</p>
            <p className="mt-1 text-sm text-muted-foreground">Subject-first workspace</p>
            <p className="mt-3 text-xs text-muted-foreground">Start in Subjects, enter one subject, then use all study features inside that context.</p>
          </div>
          <SidebarNav />
        </aside>
        <div className="flex min-h-screen flex-col">
          <TopToolbar />
          <main className="page-enter flex-1 px-4 py-6 lg:px-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
