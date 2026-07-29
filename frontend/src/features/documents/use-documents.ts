"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import {
  deleteDocument,
  listDocuments,
  uploadDocument,
  type DocumentDto,
} from "@/lib/api/documents";
import { getJob } from "@/lib/api/jobs";

export function useSubjectDocuments(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);

  return useQuery({
    queryKey: ["documents", subjectId, token],
    queryFn: async () => {
      const data = await listDocuments(token, subjectId);
      return data.items;
    },
    enabled: authResolved && Boolean(token) && Boolean(subjectId),
    refetchInterval: (query) => {
      const items = query.state.data as DocumentDto[] | undefined;
      if (!items?.length) {
        return false;
      }
      const pending = items.some((d) => d.status === "queued" || d.status === "processing");
      return pending ? 2500 : false;
    },
  });
}

export function useUploadDocument(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadDocument(token, subjectId, file),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documents", subjectId] });
    },
  });
}

export function useDeleteDocument(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (documentId: string) => deleteDocument(token, documentId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["documents", subjectId] });
    },
  });
}

export function useJobStatus(jobId: string | null, enabled: boolean) {
  const token = useSessionStore((s) => s.token);

  return useQuery({
    queryKey: ["jobs", jobId, token],
    queryFn: () => getJob(token, jobId!),
    enabled: enabled && Boolean(token) && Boolean(jobId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed" || status === "cancelled") {
        return false;
      }
      return 2000;
    },
  });
}
