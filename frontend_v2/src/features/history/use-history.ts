"use client";

import { useQuery } from "@tanstack/react-query";

import { getGenerationHistory } from "@/lib/api/backend";
import type { ScopeLiteral } from "@/lib/schemas/backend";

export function useGenerationHistory(params: {
  token: string;
  scope: ScopeLiteral;
  scopeId: string;
  limit?: number;
  enabled: boolean;
}) {
  return useQuery({
    queryKey: ["generation-history", params.scope, params.scopeId, params.limit || 20],
    queryFn: () =>
      getGenerationHistory({
        token: params.token,
        scope: params.scope,
        scopeId: params.scopeId,
        limit: params.limit,
      }),
    enabled: params.enabled,
  });
}
