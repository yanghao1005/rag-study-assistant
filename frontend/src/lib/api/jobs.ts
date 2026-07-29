import { apiRequest } from "@/lib/api/http";

export type JobDto = {
  id: string;
  job_type: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  document_id?: string | null;
  subject_id?: string | null;
  error_message?: string | null;
  result?: unknown;
  stages?: Array<{
    stage: string;
    status: string;
    duration_ms: number;
    details?: Record<string, unknown>;
  }>;
};

export async function getJob(token: string, jobId: string) {
  return apiRequest<JobDto>(`/jobs/${jobId}`, { token });
}
