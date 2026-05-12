"use client";

import { useQuery } from "@tanstack/react-query";

import { getJob } from "@/lib/api/backend";

export function useJobStatus(params: { token: string; jobId: string; enabled: boolean }) {
  return useQuery({
    queryKey: ["jobs", params.jobId],
    queryFn: () => getJob({ token: params.token, jobId: params.jobId }),
    enabled: params.enabled,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "completed" || status === "failed") {
        return false;
      }
      return 2000;
    },
  });
}
