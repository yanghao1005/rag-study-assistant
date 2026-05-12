"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { toast } from "sonner";
import { ArrowLeftCircle, ChevronDown, LogOut, UserCircle2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
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
    <header className="sticky top-0 z-20 border-b bg-background/90 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="flex items-center justify-between gap-4 px-4 py-2.5 lg:px-6">
        <div className="flex min-w-0 items-center gap-3">
          {subjectId && !pathname.startsWith("/dashboard") ? (
            <Button
              type="button"
              size="sm"
              onClick={() => router.push("/dashboard")}
              className="h-8 gap-1.5 bg-primary font-semibold text-primary-foreground shadow-sm"
            >
              <ArrowLeftCircle className="size-4" />
              Change Subject
            </Button>
          ) : null}
          <div className="hidden size-8 items-center justify-center rounded-lg bg-primary/15 text-primary sm:flex">
            <UserCircle2 className="size-4" />
          </div>
          <div className="min-w-0">
            <p className="truncate text-sm font-semibold">{pageTitle}</p>
            <p className="truncate text-xs text-muted-foreground">{pageSubtitle}</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Badge variant={token ? "success" : "warning"}>{token ? "Authenticated" : "Not signed in"}</Badge>
          <div ref={menuRef} className="relative">
            <button
              type="button"
              className="flex items-center gap-2 rounded-lg border bg-background px-2 py-1.5 text-left text-xs shadow-xs transition-colors hover:bg-accent/35"
              onClick={() => setMenuOpen((value) => !value)}
            >
              <div className="grid size-7 place-items-center rounded-full bg-primary/15 text-[11px] font-semibold text-primary">{userInitials}</div>
              <div className="hidden min-w-0 sm:block">
                <p className="max-w-40 truncate font-medium">{userEmail || "Authenticated session"}</p>
              </div>
              <ChevronDown className="size-3.5 text-muted-foreground" />
            </button>

            {menuOpen ? (
              <div className="absolute right-0 top-[calc(100%+8px)] z-40 w-56 rounded-xl border bg-popover p-2 shadow-lg">
                <div className="mb-1 rounded-lg px-2 py-1.5">
                  <p className="truncate text-xs font-medium">{userEmail || "Authenticated session"}</p>
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
