"use client";

import { useMutation } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import { generateFlashcards, generateQuiz } from "@/lib/api/generation";

export function useGenerateFlashcards() {
  const token = useSessionStore((s) => s.token);
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      count?: number;
      query?: string;
      document_id?: string;
    }) => generateFlashcards(token, body),
  });
}

export function useGenerateQuiz() {
  const token = useSessionStore((s) => s.token);
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      count?: number;
      query?: string;
      document_id?: string;
      difficulty?: "easy" | "medium" | "hard";
    }) => generateQuiz(token, body),
  });
}
