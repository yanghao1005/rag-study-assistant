"use client";

import { useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn, motion } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useAskChat } from "@/features/chat/use-chat";
import { useSubjectDocuments } from "@/features/documents/use-documents";
import type { CitationDto } from "@/lib/api/chat";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: CitationDto[];
};

export function ChatPanel({ subjectId }: { subjectId: string }) {
  const { data: documents, isLoading } = useSubjectDocuments(subjectId);
  const ask = useAskChat();
  const [question, setQuestion] = useState("");
  const [threadId, setThreadId] = useState<string | undefined>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, startTransition] = useTransition();

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const q = question.trim();
    if (!q) {
      return;
    }
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");

    startTransition(async () => {
      try {
        const result = await ask.mutateAsync({
          subject_id: subjectId,
          question: q,
          thread_id: threadId,
        });
        if (result.thread_id) {
          setThreadId(result.thread_id);
        }
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: "assistant",
            content: result.answer,
            citations: result.citations,
          },
        ]);
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "No se pudo responder");
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
    <div className="mx-auto flex h-[calc(100dvh-11rem)] max-w-3xl flex-col">
      <div className="flex-1 space-y-6 overflow-y-auto pr-1">
        {messages.length === 0 ? (
          <FadeIn y={6}>
            <p className="text-sm text-muted-foreground">
              Pregunta sobre tus apuntes. Las respuestas citarán fragmentos del material.
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
              <p className="text-[17px] leading-relaxed whitespace-pre-wrap">{msg.content}</p>
              {msg.citations && msg.citations.length > 0 ? (
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
        {pending || ask.isPending ? (
          <p className="animate-pulse-soft text-sm text-muted-foreground" aria-live="polite">
            Pensando…
          </p>
        ) : null}
      </div>

      <form onSubmit={submit} className="mt-4 flex gap-2 border-t border-border pt-4">
        <Input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Pregunta sobre esta asignatura…"
          disabled={pending || ask.isPending}
        />
        <Button type="submit" className="hover-lift" disabled={pending || ask.isPending || !question.trim()}>
          Enviar
        </Button>
      </form>
    </div>
  );
}
