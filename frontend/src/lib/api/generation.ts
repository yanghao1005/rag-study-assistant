import { apiRequest } from "@/lib/api/http";

export type FlashcardDto = {
  front: string;
  back: string;
  hint?: string | null;
};

export type QuizQuestionDto = {
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

export async function getArtifact(token: string, artifactId: string) {
  return apiRequest<{
    id: string;
    artifact_type: string;
    title: string;
    cards?: FlashcardDto[];
    questions?: QuizQuestionDto[];
  }>(`/generate/artifacts/${artifactId}`, { token });
}
