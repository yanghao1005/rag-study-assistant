"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import { listDueCards, reviewCard } from "@/lib/api/planner";

export function useDueCards(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);
  return useQuery({
    queryKey: ["planner-due", subjectId, token],
    queryFn: async () => {
      const data = await listDueCards(token, subjectId);
      return data.items;
    },
    enabled: authResolved && Boolean(token) && Boolean(subjectId),
  });
}

export function useReviewCard(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: { flashcardId: string; quality: number }) =>
      reviewCard(token, payload.flashcardId, payload.quality),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["planner-due", subjectId] });
    },
  });
}
