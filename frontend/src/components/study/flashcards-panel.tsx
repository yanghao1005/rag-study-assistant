"use client";

import { useEffect, useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn, motion, useReducedMotion } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useSubjectDocuments } from "@/features/documents/use-documents";
import { useGenerateFlashcards } from "@/features/generation/use-generation";
import type { FlashcardDto } from "@/lib/api/generation";

export function FlashcardsPanel({ subjectId }: { subjectId: string }) {
  const reduce = useReducedMotion();
  const { data: documents, isLoading } = useSubjectDocuments(subjectId);
  const generate = useGenerateFlashcards();
  const [cards, setCards] = useState<FlashcardDto[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [query, setQuery] = useState("");
  const [pending, startTransition] = useTransition();

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];
  const current = cards[index];

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (!cards.length) {
        return;
      }
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        setFlipped((v) => !v);
      } else if (e.key === "ArrowRight") {
        setIndex((i) => Math.min(cards.length - 1, i + 1));
        setFlipped(false);
      } else if (e.key === "ArrowLeft") {
        setIndex((i) => Math.max(0, i - 1));
        setFlipped(false);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [cards.length]);

  function onGenerate() {
    startTransition(async () => {
      try {
        const result = await generate.mutateAsync({
          subject_id: subjectId,
          count: 8,
          query: query.trim() || undefined,
        });
        if (!result.cards.length) {
          toast.error("No se generaron tarjetas. Prueba con más material.");
          return;
        }
        setCards(result.cards);
        setIndex(0);
        setFlipped(false);
        toast.success(`${result.cards.length} flashcards listas`);
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "Error al generar");
      }
    });
  }

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (readyDocs.length === 0) {
    return (
      <EmptyState
        title="Necesitas documentos listos"
        description="Sube e indexa un PDF antes de generar flashcards."
      />
    );
  }

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center gap-6 pt-2">
      <FadeIn className="flex w-full flex-col gap-3 sm:flex-row" y={6}>
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Tema opcional (ej. fotosíntesis)"
        />
        <Button onClick={onGenerate} disabled={pending || generate.isPending}>
          {pending || generate.isPending ? "Generando…" : "Generar"}
        </Button>
      </FadeIn>

      {!current ? (
        <EmptyState
          title="Sin deck todavía"
          description="Genera un conjunto de flashcards a partir de tus documentos."
        />
      ) : (
        <>
          <p className="text-sm text-muted-foreground">
            {index + 1} / {cards.length}
          </p>
          <div className="perspective-1000 w-full">
            <motion.button
              type="button"
              key={`${index}-${flipped}`}
              onClick={() => setFlipped((v) => !v)}
              className="relative min-h-52 w-full cursor-pointer rounded-lg border border-border bg-card px-8 py-12 text-center shadow-none outline-none focus-visible:ring-2 focus-visible:ring-ring"
              animate={reduce ? undefined : { rotateY: flipped ? 180 : 0 }}
              transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
              style={{ transformStyle: "preserve-3d" }}
            >
              <span
                className="block text-lg leading-relaxed"
                style={{
                  transform: flipped && !reduce ? "rotateY(180deg)" : undefined,
                  backfaceVisibility: "hidden",
                }}
              >
                {flipped ? current.back : current.front}
              </span>
            </motion.button>
          </div>
          <p className="text-xs text-muted-foreground">Space / Enter girar · ← → navegar</p>
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="hover-lift"
              disabled={index === 0}
              onClick={() => {
                setIndex((i) => Math.max(0, i - 1));
                setFlipped(false);
              }}
            >
              Anterior
            </Button>
            <Button className="hover-lift" onClick={() => setFlipped((v) => !v)}>
              Girar
            </Button>
            <Button
              variant="outline"
              className="hover-lift"
              disabled={index >= cards.length - 1}
              onClick={() => {
                setIndex((i) => Math.min(cards.length - 1, i + 1));
                setFlipped(false);
              }}
            >
              Siguiente
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
