import {
  chatAskResponseSchema,
  deleteGeneratedGroupResponseSchema,
  deleteDocumentResponseSchema,
  documentListResponseSchema,
  documentRecordSchema,
  documentUploadResponseSchema,
  generatedGroupResponseSchema,
  generateFlashcardsResponseSchema,
  generatedHistoryResponseSchema,
  generateQuizResponseSchema,
  jobSchema,
  type ChatAskResponse,
  type DeleteDocumentResponse,
  type DeleteGeneratedGroupResponse,
  type DocumentListResponse,
  type DocumentRecord,
  type DocumentUploadResponse,
  type GeneratedGroupResponse,
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

export async function listDocuments(params: {
  token: string;
  subjectId?: string;
}): Promise<DocumentListResponse> {
  const payload = await request<unknown>("/documents", {
    token: params.token,
    query: {
      subject_id: params.subjectId,
    },
  });
  return documentListResponseSchema.parse(payload);
}

export async function renameDocument(params: {
  token: string;
  documentId: string;
  filename: string;
}): Promise<DocumentRecord> {
  const payload = await request<unknown>(`/documents/${params.documentId}`, {
    method: "PATCH",
    token: params.token,
    json: {
      filename: params.filename,
    },
  });
  return documentRecordSchema.parse(payload);
}

export async function deleteDocument(params: {
  token: string;
  documentId: string;
}): Promise<DeleteDocumentResponse> {
  const payload = await request<unknown>(`/documents/${params.documentId}`, {
    method: "DELETE",
    token: params.token,
  });
  return deleteDocumentResponseSchema.parse(payload);
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
  sourceDocumentIds?: string[];
  query: string;
  count: number;
}): Promise<GenerateFlashcardsResponse> {
  const payload = await request<unknown>("/generate/flashcards", {
    method: "POST",
    token: params.token,
    json: {
      scope: params.scope,
      scope_id: params.scopeId,
      source_document_ids: params.sourceDocumentIds || [],
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
  sourceDocumentIds?: string[];
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
      source_document_ids: params.sourceDocumentIds || [],
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

export async function getGeneratedGroup(params: {
  token: string;
  groupId: string;
}): Promise<GeneratedGroupResponse> {
  const payload = await request<unknown>(`/generate/groups/${params.groupId}`, {
    token: params.token,
  });
  return generatedGroupResponseSchema.parse(payload);
}

export async function updateGeneratedGroup(params: {
  token: string;
  groupId: string;
  contentJson: Record<string, unknown>;
}): Promise<GeneratedGroupResponse> {
  const payload = await request<unknown>(`/generate/groups/${params.groupId}`, {
    method: "PATCH",
    token: params.token,
    json: {
      content_json: params.contentJson,
    },
  });
  return generatedGroupResponseSchema.parse(payload);
}

export async function deleteGeneratedGroup(params: {
  token: string;
  groupId: string;
}): Promise<DeleteGeneratedGroupResponse> {
  const payload = await request<unknown>(`/generate/groups/${params.groupId}`, {
    method: "DELETE",
    token: params.token,
  });
  return deleteGeneratedGroupResponseSchema.parse(payload);
}
