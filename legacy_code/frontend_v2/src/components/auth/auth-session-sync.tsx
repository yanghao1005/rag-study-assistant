"use client";

import { useEffect } from "react";

import { useSessionStore } from "@/features/auth/session-store";
import { getSupabaseBrowserClient } from "@/lib/supabase/client";

export function AuthSessionSync() {
  const { setAuthResolved, setAuthSession, setToken, setUser } = useSessionStore();

  useEffect(() => {
    let supabase;
    try {
      supabase = getSupabaseBrowserClient();
    } catch {
      setToken("");
      setUser({ userId: "", userEmail: "" });
      setAuthResolved(true);
      return;
    }

    const bootstrap = async () => {
      const { data } = await supabase.auth.getSession();
      const session = data.session;
      if (session?.access_token && session.user) {
        setAuthSession({
          token: session.access_token,
          userId: session.user.id,
          userEmail: session.user.email ?? "",
        });
      } else {
        setToken("");
        setUser({ userId: "", userEmail: "" });
        setAuthResolved(true);
      }
    };

    void bootstrap();

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session?.access_token && session.user) {
        setAuthSession({
          token: session.access_token,
          userId: session.user.id,
          userEmail: session.user.email ?? "",
        });
        return;
      }

      setToken("");
      setUser({ userId: "", userEmail: "" });
      setAuthResolved(true);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [setAuthResolved, setAuthSession, setToken, setUser]);

  return null;
}
