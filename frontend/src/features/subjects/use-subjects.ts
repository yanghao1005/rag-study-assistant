"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import {
  createSubject,
  deleteSubject,
  listSubjects,
  updateSubject,
} from "@/lib/api/subjects";

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

export function useCreateSubject() {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (body: { name: string; description?: string; color?: string }) =>
      createSubject(token, body),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["subjects"] });
    },
  });
}

export function useUpdateSubject() {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (input: {
      subjectId: string;
      name?: string;
      description?: string | null;
    }) =>
      updateSubject(token, input.subjectId, {
        name: input.name,
        description: input.description,
      }),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["subjects"] });
    },
  });
}

export function useDeleteSubject() {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (subjectId: string) => deleteSubject(token, subjectId),
    onSuccess: async (_data, subjectId) => {
      await queryClient.invalidateQueries({ queryKey: ["subjects"] });
      queryClient.removeQueries({ queryKey: ["documents", subjectId] });
    },
  });
}
