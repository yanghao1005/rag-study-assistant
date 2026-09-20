"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { deleteGeneratedGroup, getGeneratedGroup, updateGeneratedGroup } from "@/lib/api/backend";

export function useGeneratedGroup(params: { token: string; groupId: string; enabled?: boolean }) {
  return useQuery({
    queryKey: ["generated-group", params.groupId],
    queryFn: () => getGeneratedGroup({ token: params.token, groupId: params.groupId }),
    enabled: Boolean(params.token && params.groupId && (params.enabled ?? true)),
  });
}

export function useUpdateGeneratedGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateGeneratedGroup,
    onSuccess: (response, variables) => {
      queryClient.setQueryData(["generated-group", variables.groupId], response);
      queryClient.invalidateQueries({ queryKey: ["generation-history"] });
    },
  });
}

export function useDeleteGeneratedGroup() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteGeneratedGroup,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["generation-history"] });
    },
  });
}
