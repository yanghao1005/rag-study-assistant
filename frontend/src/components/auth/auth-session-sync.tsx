"use client";

import { useEffect } from "react";

import { useSessionStore } from "@/features/auth/session-store";
import { createClient } from "@/lib/supabase/client";

export function AuthSessionSync() {
  const hydrate = useSessionStore((s) => s.hydrate);
  const setAuthSession = useSessionStore((s) => s.setAuthSession);
  const setAuthResolved = useSessionStore((s) => s.setAuthResolved);
  const clear = useSessionStore((s) => s.clear);

  useEffect(() => {
    hydrate();
    const supabase = createClient();

    void supabase.auth.getSession().then(({ data }) => {
      const session = data.session;
      if (session?.access_token && session.user) {
        setAuthSession({
          token: session.access_token,
          userId: session.user.id,
          userEmail: session.user.email || "",
        });
      } else {
        setAuthResolved(true);
      }
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.access_token && session.user) {
        setAuthSession({
          token: session.access_token,
          userId: session.user.id,
          userEmail: session.user.email || "",
        });
      } else {
        clear();
      }
    });

    return () => subscription.unsubscribe();
  }, [hydrate, setAuthSession, setAuthResolved, clear]);

  return null;
}
