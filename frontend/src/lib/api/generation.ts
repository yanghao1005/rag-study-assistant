import { apiRequest } from "@/lib/api/http";

export type ArtifactOrigin = "generated" | "manual" | "imported";

export type FlashcardDto = {
  id?: string;
  front: string;
  back: string;
  hint?: string | null;
};

export type QuizQuestionDto = {
  id?: string;
  question: string;
  options: string[];
  correct_option_index: number;
  explanation?: string | null;
};

export async function generateFlashcards(
  token: string,
  body: {
    subject_id: string;
    count?: number;
    query?: string;
    document_id?: string;
    document_ids?: string[];
    save?: boolean;
  },
) {
  return apiRequest<{ artifact_id: string | null; cards: FlashcardDto[] }>("/generate/flashcards", {
    method: "POST",
    token,
    json: body,
  });
}

export async function generateQuiz(
  token: string,
  body: {
    subject_id: string;
    count?: number;
    query?: string;
    document_id?: string;
    document_ids?: string[];
    difficulty?: "easy" | "medium" | "hard";
    save?: boolean;
  },
) {
  return apiRequest<{ artifact_id: string | null; questions: QuizQuestionDto[] }>("/generate/quiz", {
    method: "POST",
    token,
    json: body,
  });
}

export type ArtifactSummaryDto = {
  id: string;
  artifact_type: string;
  title: string;
  status: string;
  subject_id: string;
    created_at?: string | null;
  updated_at?: string | null;
  item_count?: number;
  origin?: ArtifactOrigin;
};

export async function listArtifacts(
  token: string,
  subjectId: string,
  artifactType?: string,
) {
  return apiRequest<{ items: ArtifactSummaryDto[] }>("/generate/artifacts", {
    token,
    query: {
      subject_id: subjectId,
      artifact_type: artifactType,
    },
  });
}

export async function createArtifact(
  token: string,
  body: {
    subject_id: string;
    artifact_type: "flashcard_deck" | "quiz";
    title?: string;
    origin?: "manual" | "imported";
    cards?: FlashcardDto[];
    questions?: QuizQuestionDto[];
  },
) {
  return apiRequest<ArtifactSummaryDto>("/generate/artifacts", {
    method: "POST",
    token,
    json: body,
  });
}

export async function updateArtifact(token: string, artifactId: string, title: string) {
  return apiRequest<ArtifactSummaryDto>(`/generate/artifacts/${artifactId}`, {
    method: "PATCH",
    token,
    json: { title },
  });
}

export async function deleteArtifact(token: string, artifactId: string) {
  return apiRequest<{ deleted: boolean }>(`/generate/artifacts/${artifactId}`, {
    method: "DELETE",
    token,
  });
}

export async function addFlashcard(
  token: string,
  artifactId: string,
  body: { front: string; back: string; hint?: string | null },
) {
  return apiRequest<FlashcardDto>(`/generate/artifacts/${artifactId}/flashcards`, {
    method: "POST",
    token,
    json: body,
  });
}

export async function updateFlashcard(
  token: string,
  artifactId: string,
  cardId: string,
  body: { front: string; back: string; hint?: string | null },
) {
  return apiRequest<FlashcardDto>(`/generate/artifacts/${artifactId}/flashcards/${cardId}`, {
    method: "PATCH",
    token,
    json: body,
  });
}

export async function deleteFlashcard(token: string, artifactId: string, cardId: string) {
  return apiRequest<{ deleted: boolean }>(
    `/generate/artifacts/${artifactId}/flashcards/${cardId}`,
    { method: "DELETE", token },
  );
}

export async function addQuizQuestion(
  token: string,
  artifactId: string,
  body: {
    question: string;
    options: string[];
    correct_option_index: number;
    explanation?: string | null;
  },
) {
  return apiRequest<QuizQuestionDto>(`/generate/artifacts/${artifactId}/questions`, {
    method: "POST",
    token,
    json: body,
  });
}

export async function updateQuizQuestion(
  token: string,
  artifactId: string,
  questionId: string,
  body: {
    question: string;
    options: string[];
    correct_option_index: number;
    explanation?: string | null;
  },
) {
  return apiRequest<QuizQuestionDto>(
    `/generate/artifacts/${artifactId}/questions/${questionId}`,
    { method: "PATCH", token, json: body },
  );
}

export async function deleteQuizQuestion(token: string, artifactId: string, questionId: string) {
  return apiRequest<{ deleted: boolean }>(
    `/generate/artifacts/${artifactId}/questions/${questionId}`,
    { method: "DELETE", token },
  );
}

export async function getArtifact(token: string, artifactId: string) {
  return apiRequest<{
    id: string;
    artifact_type: string;
    title: string;
    cards?: FlashcardDto[];
    questions?: QuizQuestionDto[];
  }>(`/generate/artifacts/${artifactId}`, { token });
}
