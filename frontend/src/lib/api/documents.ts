import { apiRequest } from "@/lib/api/http";

export type DocumentDto = {
  id: string;
  subject_id: string;
  filename: string;
  status: "queued" | "processing" | "ready" | "error";
  total_pages: number;
  file_size: number;
  error_message?: string | null;
  storage_path?: string;
};

export type UploadDocumentResponse = {
  document_id: string;
  job_id: string;
  status: string;
  filename: string;
};

export async function listDocuments(token: string, subjectId: string) {
  return apiRequest<{ items: DocumentDto[] }>("/documents", {
    token,
    query: { subject_id: subjectId },
  });
}

export async function getDocument(token: string, documentId: string) {
  return apiRequest<DocumentDto>(`/documents/${documentId}`, { token });
}

export async function deleteDocument(token: string, documentId: string) {
  return apiRequest<{ deleted: boolean }>(`/documents/${documentId}`, {
    method: "DELETE",
    token,
  });
}

export async function uploadDocument(token: string, subjectId: string, file: File) {
  const form = new FormData();
  form.append("subject_id", subjectId);
  form.append("file", file);
  return apiRequest<UploadDocumentResponse>("/documents/upload", {
    method: "POST",
    token,
    body: form,
  });
}
