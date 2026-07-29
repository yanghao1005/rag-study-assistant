"use client";

import { useMutation } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import { askChat } from "@/lib/api/chat";

export function useAskChat() {
  const token = useSessionStore((s) => s.token);

  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      question: string;
      thread_id?: string;
      document_id?: string;
    }) => askChat(token, body),
  });
}
