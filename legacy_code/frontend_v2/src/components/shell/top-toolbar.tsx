"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeftCircle, ChevronDown, LogOut } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useSessionStore } from "@/features/auth/session-store";
import { useSubjects } from "@/features/subjects/use-subjects";
import { getSupabaseBrowserClient } from "@/lib/supabase/client";

export function TopToolbar() {
  const pathname = usePathname();
  const router = useRouter();
  const { token, userEmail, subjectId, hydrated, hydrate, clear } = useSessionStore();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);
  const subjectsQuery = useSubjects(Boolean(token));

  const activeSubjectName = useMemo(() => {
    if (!subjectId) {
      return "";
    }
    return (subjectsQuery.data || []).find((subject) => subject.id === subjectId)?.name || "";
  }, [subjectId, subjectsQuery.data]);

  const pageTitle = useMemo(() => {
    if (pathname.startsWith("/dashboard")) {
      return "Subjects";
    }
    if (!subjectId) {
      return "Subjects";
    }
    if (pathname.startsWith("/documents")) {
      return "Documents";
    }
    if (pathname.startsWith("/generate")) {
      return "Generate";
    }
    if (pathname.startsWith("/chat")) {
      return "Chat";
    }
    if (pathname.startsWith("/history")) {
      return "History";
    }
    return "Subject Workspace";
  }, [pathname, subjectId]);

  const pageSubtitle = pathname.startsWith("/dashboard")
    ? "Select a subject to enter its workspace."
    : subjectId
      ? `Current workspace: ${activeSubjectName || "Selected subject"}`
      : "Select a subject to open the workspace.";

  const userInitials = useMemo(() => {
    const seed = userEmail?.trim() || "User";
    const local = seed.split("@")[0] || seed;
    const pieces = local.split(/[._\s-]+/).filter(Boolean);
    if (pieces.length === 0) {
      return "U";
    }
    if (pieces.length === 1) {
      return pieces[0].slice(0, 2).toUpperCase();
    }
    return `${pieces[0][0]}${pieces[1][0]}`.toUpperCase();
  }, [userEmail]);

  useEffect(() => {
    if (!hydrated) {
      hydrate();
    }
  }, [hydrate, hydrated]);

  useEffect(() => {
    const onPointerDown = (event: PointerEvent) => {
      if (!menuRef.current) {
        return;
      }
      const target = event.target;
      if (target instanceof Node && !menuRef.current.contains(target)) {
        setMenuOpen(false);
      }
    };

    window.addEventListener("pointerdown", onPointerDown);
    return () => {
      window.removeEventListener("pointerdown", onPointerDown);
    };
  }, []);

  const handleReset = () => {
    void (async () => {
      const supabase = getSupabaseBrowserClient();
      await supabase.auth.signOut();
      clear();
      router.push("/onboarding");
      toast.success("Signed out.");
    })();
  };

  return (
    <header className="sticky top-0 z-20 border-b border-[var(--sl-muted)] bg-white/85 backdrop-blur-md">
      <div className="flex items-center justify-between gap-4 px-4 py-3 lg:px-6">
        <div className="flex min-w-0 items-center gap-4">
          {subjectId && !pathname.startsWith("/dashboard") ? (
            <Button
              type="button"
              size="sm"
              onClick={() => router.push("/dashboard")}
              className="h-8 gap-1.5 rounded-sl-standard bg-[var(--sl-lavender)] text-white hover:bg-[rgba(167,139,250,0.9)]"
            >
              <ArrowLeftCircle className="size-4" />
              Change Subject
            </Button>
          ) : null}
          <div className="min-w-0">
            <p className="truncate text-lg font-semibold text-[var(--sl-text-primary)]">{pageTitle}</p>
            <p className="truncate text-xs text-[var(--sl-text-secondary)]">{pageSubtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div ref={menuRef} className="relative">
            <button
              type="button"
              className="flex items-center gap-2 rounded-sl-standard border border-[var(--sl-muted)] bg-white px-2 py-1.5 text-left text-xs transition-colors hover:bg-[var(--sl-muted)]"
              onClick={() => setMenuOpen((value) => !value)}
            >
              <div className="grid size-7 place-items-center rounded-full bg-[rgba(167,139,250,0.18)] text-[11px] font-semibold text-[var(--sl-lavender)]">{userInitials}</div>
              <div className="hidden min-w-0 sm:block">
                <p className="max-w-40 truncate font-medium text-[var(--sl-text-primary)]">{userEmail || "Authenticated session"}</p>
              </div>
              <ChevronDown className="size-3.5 text-[var(--sl-text-secondary)]" />
            </button>

            {menuOpen ? (
              <div className="absolute right-0 top-[calc(100%+8px)] z-40 w-56 rounded-xl border border-[var(--sl-muted)] bg-white p-2 shadow-sl-sm">
                <div className="mb-1 rounded-lg px-2 py-1.5">
                  <p className="truncate text-xs font-medium text-[var(--sl-text-primary)]">{userEmail || "Authenticated session"}</p>
                </div>
                <Button type="button" size="sm" variant="ghost" className="w-full justify-start" onClick={handleReset}>
                  <LogOut className="size-3.5" />
                  Sign Out
                </Button>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
}
