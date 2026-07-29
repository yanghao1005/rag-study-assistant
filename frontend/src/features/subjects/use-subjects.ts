"use client";

import { useQuery } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import { listSubjects } from "@/lib/api/subjects";

export function useSubjects() {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);

  return useQuery({
    queryKey: ["subjects", token],
    queryFn: async () => {
      const data = await listSubjects(token);
      return data.items;
    },
    enabled: authResolved && Boolean(token),
  });
}
