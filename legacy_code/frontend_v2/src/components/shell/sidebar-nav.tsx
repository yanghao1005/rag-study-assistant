"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  BookCopy,
  FileText,
  FolderOpen,
  History,
  LayoutDashboard,
  MessageSquare,
  PenSquare,
  Shield,
  Sparkles,
} from "lucide-react";

import { useSessionStore } from "@/features/auth/session-store";
import { FEATURE_REGISTRY } from "@/lib/constants/features";
import { cn } from "@/lib/utils/cn";

export function SidebarNav() {
  const pathname = usePathname();
  const { hydrated, hydrate, subjectId } = useSessionStore();
  const inDashboard = pathname === "/dashboard" || pathname.startsWith("/dashboard/");

  const iconMap: Record<string, React.ReactNode> = {
    dashboard: <LayoutDashboard className="size-4" />,
    subject: <FolderOpen className="size-4" />,
    documents: <FileText className="size-4" />,
    generate: <Sparkles className="size-4" />,
    flashcards: <BookCopy className="size-4" />,
    quizzes: <PenSquare className="size-4" />,
    chat: <MessageSquare className="size-4" />,
    history: <History className="size-4" />,
  };

  useEffect(() => {
    if (!hydrated) {
      hydrate();
    }
  }, [hydrate, hydrated]);

  return (
    <nav className="flex h-full flex-col">
      <div className="space-y-1">
        {FEATURE_REGISTRY.map((item) => {
          if (!item.enabled) {
            return null;
          }

          if (inDashboard && item.key !== "dashboard") {
            return null;
          }

          if (!inDashboard && !subjectId && item.key !== "dashboard") {
            return null;
          }

          if (!inDashboard && subjectId && item.key === "dashboard") {
            return null;
          }

          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.key}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 rounded-sl-standard border-l-2 px-3 py-2 text-sm transition-all",
                active
                  ? "border-l-[var(--sl-lavender)] bg-[rgba(167,139,250,0.12)] text-[var(--sl-lavender)]"
                  : "border-l-transparent text-[var(--sl-text-secondary)] hover:bg-[var(--sl-muted)] hover:text-[var(--sl-text-primary)]",
              )}
            >
              <span>{iconMap[item.key] || <BookOpen className="size-4" />}</span>
              <span>{item.title}</span>
            </Link>
          );
        })}
      </div>

      <div className="mt-auto border-t border-[var(--sl-muted)] pt-3">
        <Link
          href="/admin"
          className="flex items-center gap-2.5 rounded-sl-standard px-3 py-2 text-sm text-[var(--sl-text-secondary)] transition-colors hover:bg-[var(--sl-muted)] hover:text-[var(--sl-text-primary)]"
        >
          <Shield className="size-4" />
          Admin
        </Link>
      </div>
    </nav>
  );
}
