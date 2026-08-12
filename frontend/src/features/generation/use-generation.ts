"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import {
  generateFlashcards,
  generateQuiz,
  getArtifact,
  listArtifacts,
} from "@/lib/api/generation";

export function useGenerateFlashcards() {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      count?: number;
      query?: string;
      document_id?: string;
    }) => generateFlashcards(token, body),
    onSuccess: async (_data, vars) => {
      await queryClient.invalidateQueries({
        queryKey: ["artifacts", vars.subject_id],
      });
    },
  });
}

export function useGenerateQuiz() {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      count?: number;
      query?: string;
      document_id?: string;
      difficulty?: "easy" | "medium" | "hard";
    }) => generateQuiz(token, body),
    onSuccess: async (_data, vars) => {
      await queryClient.invalidateQueries({
        queryKey: ["artifacts", vars.subject_id],
      });
    },
  });
}

export function useArtifacts(subjectId: string, artifactType?: string) {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);
  return useQuery({
    queryKey: ["artifacts", subjectId, artifactType, token],
    queryFn: async () => {
      const data = await listArtifacts(token, subjectId, artifactType);
      return data.items;
    },
    enabled: authResolved && Boolean(token) && Boolean(subjectId),
  });
}

export function useLoadArtifact() {
  const token = useSessionStore((s) => s.token);
  return useMutation({
    mutationFn: (artifactId: string) => getArtifact(token, artifactId),
  });
}
