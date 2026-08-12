import { apiRequest, ApiError, baseUrlCandidatesForExport } from "@/lib/api/http";

export type CitationDto = {
  index: number;
  chunk_id: string;
  document_id: string;
  page_start?: number | null;
  score?: number | null;
};

export type ChatAskResponse = {
  answer: string;
  citations: CitationDto[];
  thread_id?: string | null;
  model?: string;
  usage?: Record<string, number>;
};

export type ChatThreadDto = {
  id: string;
  title: string;
  subject_id: string;
  updated_at?: string | null;
  created_at?: string | null;
};

export type ChatMessageDto = {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations?: CitationDto[];
  created_at?: string | null;
};

export type StreamHandlers = {
  onMeta?: (meta: { thread_id?: string | null; citations: CitationDto[] }) => void;
  onToken?: (token: string) => void;
  onDone?: (payload: { answer: string; thread_id?: string | null }) => void;
  onError?: (message: string) => void;
};

export async function askChat(
  token: string,
  body: {
    subject_id: string;
    question: string;
    thread_id?: string;
    document_id?: string;
    save?: boolean;
  },
) {
  return apiRequest<ChatAskResponse>("/chat/ask", {
    method: "POST",
    token,
    json: body,
  });
}

export async function listChatThreads(token: string, subjectId: string) {
  return apiRequest<{ items: ChatThreadDto[] }>("/chat/threads", {
    token,
    query: { subject_id: subjectId },
  });
}

export async function listChatMessages(token: string, threadId: string) {
  return apiRequest<{ items: ChatMessageDto[] }>(`/chat/threads/${threadId}/messages`, {
    token,
  });
}

export async function askChatStream(
  token: string,
  body: {
    subject_id: string;
    question: string;
    thread_id?: string;
    document_id?: string;
    save?: boolean;
  },
  handlers: StreamHandlers,
) {
  let lastNetworkError: unknown = null;
  for (const base of baseUrlCandidatesForExport()) {
    try {
      const response = await fetch(`${base}/chat/ask/stream`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok || !response.body) {
        const text = await response.text();
        let message = `Request failed (${response.status})`;
        try {
          const payload = JSON.parse(text) as { message?: string };
          if (payload.message) {
            message = payload.message;
          }
        } catch {
          /* keep default */
        }
        throw new ApiError(message, response.status, text);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        buffer += decoder.decode(value, { stream: true });
        const chunks = buffer.split("\n\n");
        buffer = chunks.pop() || "";
        for (const chunk of chunks) {
          const line = chunk
            .split("\n")
            .map((l) => l.trim())
            .find((l) => l.startsWith("data:"));
          if (!line) {
            continue;
          }
          const raw = line.slice(5).trim();
          if (!raw) {
            continue;
          }
          try {
            const event = JSON.parse(raw) as {
              type: string;
              content?: string;
              citations?: CitationDto[];
              thread_id?: string | null;
              answer?: string;
              message?: string;
            };
            if (event.type === "meta") {
              handlers.onMeta?.({
                thread_id: event.thread_id,
                citations: event.citations || [],
              });
            } else if (event.type === "token" && event.content) {
              handlers.onToken?.(event.content);
            } else if (event.type === "done") {
              handlers.onDone?.({
                answer: event.answer || "",
                thread_id: event.thread_id,
              });
            } else if (event.type === "error") {
              handlers.onError?.(event.message || "Error en el stream");
            }
          } catch {
            /* ignore malformed event */
          }
        }
      }
      return;
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      lastNetworkError = error;
    }
  }

  throw new ApiError(
    "No se pudo conectar con el backend para streaming.",
    0,
    lastNetworkError,
  );
}
