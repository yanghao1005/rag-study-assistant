"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { FadeIn, motion, useReducedMotion } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { DocumentScopePicker } from "@/components/documents/document-scope-picker";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useSubjectDocuments } from "@/features/documents/use-documents";
import {
  documentScopePayload,
  useSelectedDocumentIds,
} from "@/features/documents/use-document-scope";
import {
  useArtifacts,
  useGenerateFlashcards,
  useLoadArtifact,
} from "@/features/generation/use-generation";
import type { FlashcardDto } from "@/lib/api/generation";

export function FlashcardsPanel({ subjectId }: { subjectId: string }) {
  const reduce = useReducedMotion();
  const { data: documents, isLoading } = useSubjectDocuments(subjectId);
  const generate = useGenerateFlashcards();
  const loadArtifact = useLoadArtifact();
  const { data: artifacts } = useArtifacts(subjectId, "flashcard_deck");
  const selectedDocumentIds = useSelectedDocumentIds(subjectId);
  const [cards, setCards] = useState<FlashcardDto[]>([]);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [query, setQuery] = useState("");

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];
  const current = cards[index];
  const generating = generate.isPending;

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

  async function onGenerate() {
    try {
      const result = await generate.mutateAsync({
        subject_id: subjectId,
        count: 8,
        query: query.trim() || undefined,
        ...documentScopePayload(selectedDocumentIds),
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
  }

  async function onOpenArtifact(artifactId: string) {
    try {
      const artifact = await loadArtifact.mutateAsync(artifactId);
      if (!artifact.cards?.length) {
        toast.error("Este deck no tiene tarjetas.");
        return;
      }
      setCards(artifact.cards);
      setIndex(0);
      setFlipped(false);
      toast.success("Deck cargado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo cargar");
    }
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
      <div className="w-full">
        <DocumentScopePicker subjectId={subjectId} documents={readyDocs} />
      </div>
      <FadeIn className="flex w-full flex-col gap-3 sm:flex-row" y={6}>
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Concepto del temario (ej. BMC, cadena de valor)"
        />
        <Button onClick={() => void onGenerate()} disabled={generating}>
          {generating ? "Generando…" : "Generar"}
        </Button>
      </FadeIn>

      {artifacts && artifacts.length > 0 ? (
        <div className="flex w-full flex-wrap gap-2">
          {artifacts.slice(0, 6).map((item) => (
            <Button
              key={item.id}
              type="button"
              variant="outline"
              size="sm"
              className="hover-lift"
              disabled={generating || loadArtifact.isPending}
              onClick={() => void onOpenArtifact(item.id)}
            >
              {item.title || "Deck"}
            </Button>
          ))}
        </div>
      ) : null}

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
