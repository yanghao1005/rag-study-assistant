"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import {
  addFlashcard,
  addQuizQuestion,
  createArtifact,
  deleteArtifact,
  deleteFlashcard,
  deleteQuizQuestion,
  generateFlashcards,
  generateQuiz,
  getArtifact,
  listArtifacts,
  updateArtifact,
  updateFlashcard,
  updateQuizQuestion,
  type FlashcardDto,
  type QuizQuestionDto,
} from "@/lib/api/generation";

function useInvalidateArtifacts() {
  const queryClient = useQueryClient();
  return (subjectId: string) =>
    queryClient.invalidateQueries({
      queryKey: ["artifacts", subjectId],
    });
}

export function useGenerateFlashcards() {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      count?: number;
      query?: string;
      document_id?: string;
      document_ids?: string[];
    }) => generateFlashcards(token, body),
    onSuccess: async (_data, vars) => {
      await invalidate(vars.subject_id);
    },
  });
}

export function useGenerateQuiz() {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      count?: number;
      query?: string;
      document_id?: string;
      document_ids?: string[];
      difficulty?: "easy" | "medium" | "hard";
    }) => generateQuiz(token, body),
    onSuccess: async (_data, vars) => {
      await invalidate(vars.subject_id);
    },
  });
}

export function useArtifacts(subjectId: string, artifactType?: string) {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);
  return useQuery({
    queryKey: ["artifacts", subjectId, artifactType, token],
    queryFn: async () => {
      const data = await listArtifacts(token, subjectId, artifactType);
      return data.items;
    },
    enabled: authResolved && Boolean(token) && Boolean(subjectId),
  });
}

export function useLoadArtifact() {
  const token = useSessionStore((s) => s.token);
  return useMutation({
    mutationFn: (artifactId: string) => getArtifact(token, artifactId),
  });
}

export function useCreateArtifact() {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      artifact_type: "flashcard_deck" | "quiz";
      title?: string;
      origin?: "manual" | "imported";
      cards?: FlashcardDto[];
      questions?: QuizQuestionDto[];
    }) => createArtifact(token, body),
    onSuccess: async (_data, vars) => {
      await invalidate(vars.subject_id);
    },
  });
}

export function useRenameArtifact(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: { artifactId: string; title: string }) =>
      updateArtifact(token, vars.artifactId, vars.title),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useDeleteArtifact(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (artifactId: string) => deleteArtifact(token, artifactId),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useAddFlashcard(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: {
      artifactId: string;
      front: string;
      back: string;
      hint?: string | null;
    }) => addFlashcard(token, vars.artifactId, vars),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useUpdateFlashcard(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: {
      artifactId: string;
      cardId: string;
      front: string;
      back: string;
      hint?: string | null;
    }) => updateFlashcard(token, vars.artifactId, vars.cardId, vars),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useDeleteFlashcard(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: { artifactId: string; cardId: string }) =>
      deleteFlashcard(token, vars.artifactId, vars.cardId),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useAddQuizQuestion(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: {
      artifactId: string;
      question: string;
      options: string[];
      correct_option_index: number;
      explanation?: string | null;
    }) => addQuizQuestion(token, vars.artifactId, vars),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useUpdateQuizQuestion(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: {
      artifactId: string;
      questionId: string;
      question: string;
      options: string[];
      correct_option_index: number;
      explanation?: string | null;
    }) => updateQuizQuestion(token, vars.artifactId, vars.questionId, vars),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}

export function useDeleteQuizQuestion(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const invalidate = useInvalidateArtifacts();
  return useMutation({
    mutationFn: (vars: { artifactId: string; questionId: string }) =>
      deleteQuizQuestion(token, vars.artifactId, vars.questionId),
    onSuccess: async () => {
      await invalidate(subjectId);
    },
  });
}
