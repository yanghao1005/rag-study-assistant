"use client";

import { useQuery } from "@tanstack/react-query";

import { getGenerationHistory } from "@/lib/api/backend";
import type { ScopeLiteral } from "@/lib/schemas/backend";

function isValidScopeId(value: string): boolean {
  const normalized = value.trim().toLowerCase();
  return Boolean(normalized) && normalized !== "undefined" && normalized !== "null";
}

export function useGenerationHistory(params: {
  token: string;
  scope: ScopeLiteral;
  scopeId: string;
  limit?: number;
  enabled: boolean;
}) {
  const scopeId = params.scopeId.trim();
  const canQuery = isValidScopeId(scopeId);

  return useQuery({
    queryKey: ["generation-history", params.scope, scopeId, params.limit || 20],
    queryFn: () =>
      getGenerationHistory({
        token: params.token,
        scope: params.scope,
        scopeId,
        limit: params.limit,
      }),
    enabled: params.enabled && canQuery,
    retry: 0,
  });
}
