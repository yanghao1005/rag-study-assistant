"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { deleteDocument, listDocuments, renameDocument } from "@/lib/api/backend";

export function documentsQueryKey(subjectId?: string) {
  return ["documents", subjectId || "all"] as const;
}

export function useSubjectDocuments(params: { token: string; subjectId?: string; enabled: boolean }) {
  return useQuery({
    queryKey: documentsQueryKey(params.subjectId),
    queryFn: () => listDocuments({ token: params.token, subjectId: params.subjectId }),
    enabled: params.enabled,
    refetchInterval: (query) => {
      const items = query.state.data?.items || [];
      const hasProcessing = items.some((item) => {
        const status = (item.status || "").toLowerCase();
        return status === "processing" || status === "queued" || status === "running";
      });
      return hasProcessing ? 3000 : false;
    },
  });
}

export function useRenameDocument(subjectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: renameDocument,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: documentsQueryKey(subjectId) });
    },
  });
}

export function useDeleteDocument(subjectId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteDocument,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: documentsQueryKey(subjectId) });
    },
  });
}
