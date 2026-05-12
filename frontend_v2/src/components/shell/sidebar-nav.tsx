"use client";

import { useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { useSessionStore } from "@/features/auth/session-store";
import { FEATURE_REGISTRY } from "@/lib/constants/features";
import { cn } from "@/lib/utils/cn";

export function SidebarNav() {
  const pathname = usePathname();
  const { hydrated, hydrate, subjectId } = useSessionStore();
  const inDashboard = pathname === "/dashboard" || pathname.startsWith("/dashboard/");

  useEffect(() => {
    if (!hydrated) {
      hydrate();
    }
  }, [hydrate, hydrated]);

  return (
    <nav className="flex flex-col gap-1">
      {FEATURE_REGISTRY.map((item) => {
        if (!item.enabled) {
          return null;
        }

        if (inDashboard) {
          if (item.key !== "dashboard") {
            return null;
          }
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
              "rounded-lg px-3 py-2 text-sm transition-colors",
              active ? "bg-sidebar-primary text-sidebar-primary-foreground" : "text-foreground hover:bg-sidebar-accent",
            )}
          >
            <span>{item.title}</span>
          </Link>
        );
      })}
    </nav>
  );
}
