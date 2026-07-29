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
