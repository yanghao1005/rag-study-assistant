"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { useSessionStore } from "@/features/auth/session-store";

export function WorkspaceGuard({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { hydrated, authResolved, token, hydrate } = useSessionStore();

  useEffect(() => {
    if (!hydrated) {
      hydrate();
    }
  }, [hydrated, hydrate]);

  useEffect(() => {
    if (!hydrated || !authResolved) {
      return;
    }

    if (!token) {
      const nextPath = pathname && pathname.startsWith("/") ? pathname : "/dashboard";
      router.replace(`/onboarding?next=${encodeURIComponent(nextPath)}`);
    }
  }, [authResolved, hydrated, pathname, router, token]);

  if (!hydrated || !authResolved) {
    return <div className="px-6 py-8 text-sm text-muted-foreground">Loading workspace session...</div>;
  }

  if (!token) {
    return <div className="px-6 py-8 text-sm text-muted-foreground">Redirecting to onboarding...</div>;
  }

  return <>{children}</>;
}
