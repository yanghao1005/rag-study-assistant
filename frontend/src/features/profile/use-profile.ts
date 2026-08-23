"use client";

import { useQuery } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import { getProfile } from "@/lib/api/profile";

export function useProfile() {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);

  return useQuery({
    queryKey: ["profile", token],
    queryFn: () => getProfile(token),
    enabled: authResolved && Boolean(token),
  });
}
