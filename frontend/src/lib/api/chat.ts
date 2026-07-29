import { apiRequest } from "@/lib/api/http";

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
