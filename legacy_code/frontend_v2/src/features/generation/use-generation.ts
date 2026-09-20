"use client";

import { useMutation } from "@tanstack/react-query";

import { generateFlashcards, generateQuiz } from "@/lib/api/backend";

export function useGenerateFlashcards() {
  return useMutation({
    mutationFn: generateFlashcards,
  });
}

export function useGenerateQuiz() {
  return useMutation({
    mutationFn: generateQuiz,
  });
}
