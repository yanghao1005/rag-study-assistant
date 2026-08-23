import { apiRequest } from "@/lib/api/http";

export type DueCardDto = {
  flashcard_id: string;
  front: string;
  back: string;
  hint?: string | null;
  artifact_title: string;
  next_review_at?: string | null;
  repetitions: number;
};

export async function listDueCards(token: string, subjectId: string) {
  return apiRequest<{ items: DueCardDto[] }>("/planner/due", {
    token,
    query: { subject_id: subjectId },
  });
}

export async function reviewCard(token: string, flashcardId: string, quality: number) {
  return apiRequest<{
    flashcard_id: string;
    ease: number;
    interval_days: number;
    repetitions: number;
    next_review_at?: string | null;
  }>("/planner/review", {
    method: "POST",
    token,
    json: { flashcard_id: flashcardId, quality },
  });
}
