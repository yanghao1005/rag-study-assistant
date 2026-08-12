"use client";

import { useEffect, useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn, motion } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { useSessionStore } from "@/features/auth/session-store";
import {
  streamAsk,
  useChatMessages,
  useChatThreads,
  useInvalidateChatHistory,
} from "@/features/chat/use-chat";
import { useSubjectDocuments } from "@/features/documents/use-documents";
import type { CitationDto } from "@/lib/api/chat";
import { cn } from "@/lib/utils";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: CitationDto[];
};

export function ChatPanel({ subjectId }: { subjectId: string }) {
  const token = useSessionStore((s) => s.token);
  const { data: documents, isLoading } = useSubjectDocuments(subjectId);
  const { data: threads, isLoading: threadsLoading } = useChatThreads(subjectId);
  const invalidateHistory = useInvalidateChatHistory();

  const [question, setQuestion] = useState("");
  const [threadId, setThreadId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [pending, startTransition] = useTransition();

  const { data: loadedMessages } = useChatMessages(threadId);

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];

  useEffect(() => {
    if (!threadId || !loadedMessages) {
      return;
    }
    if (streaming) {
      return;
    }
    setMessages(
      loadedMessages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({
          id: m.id,
          role: m.role as "user" | "assistant",
          content: m.content,
          citations: m.citations,
        })),
    );
  }, [loadedMessages, threadId, streaming]);

  function startNewThread() {
    setThreadId(undefined);
    setMessages([]);
  }

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const q = question.trim();
    if (!q || !token) {
      return;
    }
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: q };
    const assistantId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: assistantId, role: "assistant", content: "", citations: [] },
    ]);
    setQuestion("");
    setStreaming(true);

    startTransition(async () => {
      let citations: CitationDto[] = [];
      try {
        await streamAsk(
          token,
          { subject_id: subjectId, question: q, thread_id: threadId },
          {
            onMeta: (meta) => {
              citations = meta.citations;
              if (meta.thread_id) {
                setThreadId(meta.thread_id);
              }
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, citations: meta.citations } : m,
                ),
              );
            },
            onToken: (tokenText) => {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId ? { ...m, content: m.content + tokenText } : m,
                ),
              );
            },
            onDone: (payload) => {
              if (payload.thread_id) {
                setThreadId(payload.thread_id);
              }
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantId
                    ? {
                        ...m,
                        content: payload.answer || m.content,
                        citations: citations.length ? citations : m.citations,
                      }
                    : m,
                ),
              );
              void invalidateHistory(subjectId);
            },
            onError: (message) => {
              toast.error(message);
            },
          },
        );
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "No se pudo responder");
        setMessages((prev) => prev.filter((m) => m.id !== assistantId && m.id !== userMsg.id));
      } finally {
        setStreaming(false);
      }
    });
  }

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (readyDocs.length === 0) {
    return (
      <EmptyState
        title="Todavía no hay material listo"
        description="Sube un PDF y espera a que pase a estado Listo para poder preguntar con citas."
      />
    );
  }

  return (
    <div className="mx-auto flex h-[calc(100dvh-11rem)] max-w-5xl gap-4">
      <aside className="hidden w-56 shrink-0 flex-col border-r border-border pr-3 md:flex">
        <div className="mb-3 flex items-center justify-between gap-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Historial
          </p>
          <Button type="button" variant="ghost" size="sm" className="h-7 px-2" onClick={startNewThread}>
            Nuevo
          </Button>
        </div>
        <ScrollArea className="flex-1">
          {threadsLoading ? <Skeleton className="h-16 w-full" /> : null}
          <ul className="space-y-1 pr-2">
            {(threads || []).map((thread) => (
              <li key={thread.id}>
                <button
                  type="button"
                  className={cn(
                    "w-full cursor-pointer rounded-md px-2 py-2 text-left text-sm transition-colors",
                    thread.id === threadId
                      ? "bg-accent font-medium text-accent-foreground"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                  )}
                  onClick={() => setThreadId(thread.id)}
                >
                  <span className="line-clamp-2">{thread.title || "Chat"}</span>
                </button>
              </li>
            ))}
          </ul>
          {!threadsLoading && (threads || []).length === 0 ? (
            <p className="px-1 text-xs text-muted-foreground">Aún no hay conversaciones.</p>
          ) : null}
        </ScrollArea>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex-1 space-y-6 overflow-y-auto pr-1">
          {messages.length === 0 ? (
            <FadeIn y={6}>
              <p className="text-sm text-muted-foreground">
                Pregunta sobre tus apuntes. La respuesta aparece en streaming y cita el material.
              </p>
            </FadeIn>
          ) : null}
          {messages.map((msg) =>
            msg.role === "user" ? (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 8, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                transition={{ duration: 0.25 }}
                className="ml-auto max-w-md rounded-md bg-secondary px-4 py-3 text-sm leading-relaxed"
              >
                {msg.content}
              </motion.div>
            ) : (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="max-w-2xl space-y-3"
              >
                <p className="text-[17px] leading-relaxed whitespace-pre-wrap">
                  {msg.content || (streaming ? "…" : "")}
                </p>
                {msg.citations && msg.citations.length > 0 && !streaming ? (
                  <ol className="space-y-1 border-l-2 border-primary/40 pl-4 text-sm text-muted-foreground">
                    {msg.citations.map((c) => (
                      <li key={`${c.chunk_id}-${c.index}`}>
                        [{c.index}] documento {c.document_id.slice(0, 8)}
                        {c.page_start != null ? ` · pág. ${c.page_start}` : null}
                      </li>
                    ))}
                  </ol>
                ) : null}
              </motion.div>
            ),
          )}
          {pending || streaming ? (
            <p className="animate-pulse-soft text-sm text-muted-foreground" aria-live="polite">
              Escribiendo…
            </p>
          ) : null}
        </div>

        <form onSubmit={submit} className="mt-4 flex gap-2 border-t border-border pt-4">
          <Input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Pregunta sobre esta asignatura…"
            disabled={pending || streaming}
          />
          <Button
            type="submit"
            className="hover-lift"
            disabled={pending || streaming || !question.trim()}
          >
            Enviar
          </Button>
        </form>
      </div>
    </div>
  );
}
