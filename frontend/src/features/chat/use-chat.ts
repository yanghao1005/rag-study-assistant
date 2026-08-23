"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { useSessionStore } from "@/features/auth/session-store";
import {
  askChat,
  askChatStream,
  listChatMessages,
  listChatThreads,
  type StreamHandlers,
} from "@/lib/api/chat";

export function useAskChat() {
  const token = useSessionStore((s) => s.token);
  return useMutation({
    mutationFn: (body: {
      subject_id: string;
      question: string;
      thread_id?: string;
      document_id?: string;
      document_ids?: string[];
      save?: boolean;
    }) => askChat(token, body),
  });
}

export function useChatThreads(subjectId: string) {
  const token = useSessionStore((s) => s.token);
  const authResolved = useSessionStore((s) => s.authResolved);
  return useQuery({
    queryKey: ["chat-threads", subjectId, token],
    queryFn: async () => {
      const data = await listChatThreads(token, subjectId);
      return data.items;
    },
    enabled: authResolved && Boolean(token) && Boolean(subjectId),
  });
}

export function useChatMessages(threadId: string | undefined) {
  const token = useSessionStore((s) => s.token);
  return useQuery({
    queryKey: ["chat-messages", threadId, token],
    queryFn: async () => {
      const data = await listChatMessages(token, threadId!);
      return data.items;
    },
    enabled: Boolean(token) && Boolean(threadId),
  });
}

export function useInvalidateChatHistory() {
  const queryClient = useQueryClient();
  return (subjectId: string, threadId?: string | null) => {
    void queryClient.invalidateQueries({ queryKey: ["chat-threads", subjectId] });
    if (threadId) {
      void queryClient.invalidateQueries({ queryKey: ["chat-messages", threadId] });
    }
  };
}

export async function streamAsk(
  token: string,
  body: {
    subject_id: string;
    question: string;
    thread_id?: string;
    document_id?: string;
    document_ids?: string[];
    mode?: "standard" | "agentic";
  },
  handlers: StreamHandlers,
) {
  return askChatStream(token, body, handlers);
}
