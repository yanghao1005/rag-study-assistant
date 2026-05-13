import {
  chatAskResponseSchema,
  documentUploadResponseSchema,
  generateFlashcardsResponseSchema,
  generatedHistoryResponseSchema,
  generateQuizResponseSchema,
  jobSchema,
  type ChatAskResponse,
  type DocumentUploadResponse,
  type GenerateFlashcardsResponse,
  type GeneratedHistoryResponse,
  type GenerateQuizResponse,
  type JobResponse,
  type ScopeLiteral,
} from "@/lib/schemas/backend";
import { request } from "@/lib/api/http";

export type UploadDocumentInput = {
  token: string;
  file: File;
  subjectId: string;
};

export async function uploadDocument(input: UploadDocumentInput): Promise<DocumentUploadResponse> {
  const form = new FormData();
  form.set("file", input.file);
  form.set("subject_id", input.subjectId);

  const payload = await request<unknown>("/documents/upload", {
    method: "POST",
    token: input.token,
    body: form,
  });

  return documentUploadResponseSchema.parse(payload);
}

export async function getJob(params: { token: string; jobId: string }): Promise<JobResponse> {
  const payload = await request<unknown>(`/jobs/${params.jobId}`, {
    token: params.token,
  });
  return jobSchema.parse(payload);
}

export async function generateFlashcards(params: {
  token: string;
  scope: ScopeLiteral;
  scopeId: string;
  query: string;
  count: number;
}): Promise<GenerateFlashcardsResponse> {
  const payload = await request<unknown>("/generate/flashcards", {
    method: "POST",
    token: params.token,
    json: {
      scope: params.scope,
      scope_id: params.scopeId,
      query: params.query,
      count: params.count,
      save: true,
    },
  });
  return generateFlashcardsResponseSchema.parse(payload);
}

export async function generateQuiz(params: {
  token: string;
  scope: ScopeLiteral;
  scopeId: string;
  query: string;
  count: number;
  difficulty: "easy" | "medium" | "hard";
}): Promise<GenerateQuizResponse> {
  const payload = await request<unknown>("/generate/quiz", {
    method: "POST",
    token: params.token,
    json: {
      scope: params.scope,
      scope_id: params.scopeId,
      query: params.query,
      count: params.count,
      difficulty: params.difficulty,
      save: true,
    },
  });
  return generateQuizResponseSchema.parse(payload);
}

export async function askChat(params: {
  token: string;
  scope: ScopeLiteral;
  scopeId: string;
  question: string;
}): Promise<ChatAskResponse> {
  const payload = await request<unknown>("/chat/ask", {
    method: "POST",
    token: params.token,
    json: {
      scope: params.scope,
      scope_id: params.scopeId,
      question: params.question,
      save: true,
    },
  });
  return chatAskResponseSchema.parse(payload);
}

export async function getGenerationHistory(params: {
  token: string;
  scope: ScopeLiteral;
  scopeId: string;
  limit?: number;
}): Promise<GeneratedHistoryResponse> {
  const payload = await request<unknown>("/generate/history", {
    token: params.token,
    query: {
      scope: params.scope,
      scope_id: params.scopeId,
      limit: params.limit || 20,
    },
  });
  return generatedHistoryResponseSchema.parse(payload);
}
