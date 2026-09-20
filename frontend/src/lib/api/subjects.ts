import { apiRequest } from "@/lib/api/http";

export type SubjectDto = {
  id: string;
  name: string;
  description?: string | null;
  color?: string | null;
  sort_order?: number;
};

export async function listSubjects(token: string) {
  return apiRequest<{ items: SubjectDto[] }>("/subjects", { token });
}

export async function createSubject(
  token: string,
  body: { name: string; description?: string; color?: string },
) {
  return apiRequest<SubjectDto>("/subjects", {
    method: "POST",
    token,
    json: body,
  });
}

export async function updateSubject(
  token: string,
  subjectId: string,
  body: { name?: string; description?: string | null; color?: string | null },
) {
  return apiRequest<SubjectDto>(`/subjects/${subjectId}`, {
    method: "PATCH",
    token,
    json: body,
  });
}

export async function deleteSubject(token: string, subjectId: string) {
  return apiRequest<{ deleted: boolean }>(`/subjects/${subjectId}`, {
    method: "DELETE",
    token,
  });
}
