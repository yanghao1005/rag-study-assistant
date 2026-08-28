"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { FadeIn, motion, useReducedMotion } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { DocumentScopePicker } from "@/components/documents/document-scope-picker";
import { ArtifactLibrary } from "@/components/study/artifact-library";
import { FlashcardSetEditor } from "@/components/study/flashcard-set-editor";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useSubjectDocuments } from "@/features/documents/use-documents";
import {
  documentScopePayload,
  useSelectedDocumentIds,
} from "@/features/documents/use-document-scope";
import {
  useAddFlashcard,
  useArtifacts,
  useCreateArtifact,
  useDeleteArtifact,
  useDeleteFlashcard,
  useGenerateFlashcards,
  useLoadArtifact,
  useRenameArtifact,
  useUpdateFlashcard,
} from "@/features/generation/use-generation";
import type { ArtifactSummaryDto, FlashcardDto } from "@/lib/api/generation";
import { downloadJson, slugifyFilename } from "@/lib/artifact-meta";

export function FlashcardsPanel({ subjectId }: { subjectId: string }) {
  const reduce = useReducedMotion();
  const { data: documents, isLoading: docsLoading } = useSubjectDocuments(subjectId);
  const generate = useGenerateFlashcards();
  const loadArtifact = useLoadArtifact();
  const { data: artifacts, isLoading: artifactsLoading } = useArtifacts(subjectId, "flashcard_deck");
  const createArtifact = useCreateArtifact();
  const renameArtifact = useRenameArtifact(subjectId);
  const removeArtifact = useDeleteArtifact(subjectId);
  const addCard = useAddFlashcard(subjectId);
  const editCard = useUpdateFlashcard(subjectId);
  const removeCard = useDeleteFlashcard(subjectId);
  const selectedDocumentIds = useSelectedDocumentIds(subjectId);
  const [cards, setCards] = useState<FlashcardDto[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [hintOpen, setHintOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("practice");
  const autoOpened = useRef(false);

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];
  const current = cards[index];
  const generating = generate.isPending;
  const busy =
    generating ||
    loadArtifact.isPending ||
    createArtifact.isPending ||
    renameArtifact.isPending ||
    removeArtifact.isPending ||
    addCard.isPending ||
    editCard.isPending ||
    removeCard.isPending;
  const hasLibrary = (artifacts?.length ?? 0) > 0;

  const openArtifact = useCallback(
    async (artifactId: string) => {
      const artifact = await loadArtifact.mutateAsync(artifactId);
      setActiveArtifactId(artifact.id);
      setCards(artifact.cards ?? []);
      setIndex(0);
      setFlipped(false);
      setHintOpen(false);
    },
    [loadArtifact],
  );

  useEffect(() => {
    autoOpened.current = false;
    setActiveArtifactId(null);
    setCards([]);
    setIndex(0);
    setFlipped(false);
    setHintOpen(false);
  }, [subjectId]);

  useEffect(() => {
    if (autoOpened.current || activeArtifactId || !artifacts?.length) {
      return;
    }
    autoOpened.current = true;
    void openArtifact(artifacts[0].id).catch((err: unknown) => {
      toast.error(err instanceof Error ? err.message : "No se pudo abrir el deck");
    });
  }, [artifacts, activeArtifactId, openArtifact]);

  useEffect(() => {
    setHintOpen(false);
  }, [index, activeArtifactId]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target?.closest("input, textarea, select, [contenteditable='true']")) {
        return;
      }
      if (mode !== "practice" || !cards.length) {
        return;
      }
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        setFlipped((v) => !v);
      } else if (e.key.toLowerCase() === "h") {
        if (cards[index]?.hint) {
          e.preventDefault();
          setHintOpen((v) => !v);
        }
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
  }, [cards, index, mode]);

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
      autoOpened.current = true;
      if (result.artifact_id) {
        await openArtifact(result.artifact_id);
      } else {
        setCards(result.cards);
        setIndex(0);
        setFlipped(false);
      }
      setMode("practice");
      toast.success(`${result.cards.length} flashcards listas`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al generar");
    }
  }

  async function onCreateEmpty() {
    try {
      const created = await createArtifact.mutateAsync({
        subject_id: subjectId,
        artifact_type: "flashcard_deck",
        origin: "manual",
      });
      autoOpened.current = true;
      setActiveArtifactId(created.id);
      setCards([]);
      setIndex(0);
      setFlipped(false);
      setHintOpen(false);
      setMode("edit");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo crear el deck");
    }
  }

  async function onImport(file: File) {
    try {
      const parsed = JSON.parse(await file.text()) as {
        title?: string;
        cards?: FlashcardDto[];
      };
      const imported = Array.isArray(parsed) ? parsed : parsed.cards;
      if (!Array.isArray(imported) || imported.length === 0) {
        toast.error("El JSON no contiene tarjetas.");
        return;
      }
      const cardsPayload = imported
        .map((card) => ({
          front: String(card.front || "").trim(),
          back: String(card.back || "").trim(),
          hint: card.hint ?? null,
        }))
        .filter((card) => card.front && card.back);
      if (!cardsPayload.length) {
        toast.error("El JSON no contiene tarjetas válidas.");
        return;
      }
      const created = await createArtifact.mutateAsync({
        subject_id: subjectId,
        artifact_type: "flashcard_deck",
        title: typeof parsed.title === "string" ? parsed.title : file.name.replace(/\.json$/i, ""),
        origin: "imported",
        cards: cardsPayload,
      });
      autoOpened.current = true;
      await openArtifact(created.id);
      setMode("practice");
      toast.success(`Importadas ${cardsPayload.length} tarjetas`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "JSON no válido");
    }
  }

  async function onExport(item: ArtifactSummaryDto) {
    try {
      const artifact =
        item.id === activeArtifactId
          ? { title: item.title, cards }
          : await loadArtifact.mutateAsync(item.id);
      downloadJson(`${slugifyFilename(artifact.title || item.title)}.json`, {
        title: artifact.title || item.title,
        cards: "cards" in artifact ? artifact.cards ?? cards : cards,
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo exportar");
    }
  }

  if (docsLoading && artifactsLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (readyDocs.length === 0 && !hasLibrary && !artifactsLoading) {
    return (
      <EmptyState
        title="Necesitas documentos listos"
        description="Sube e indexa un PDF antes de generar flashcards, o importa un JSON."
      />
    );
  }

  return (
    <div className="mx-auto flex h-[calc(100dvh-11rem)] max-w-5xl flex-col gap-4 md:flex-row">
      <ArtifactLibrary
        items={artifacts}
        loading={artifactsLoading}
        activeId={activeArtifactId}
        itemNoun="tarjetas"
        createLabel="Nuevo"
        emptyLabel="Aún no hay decks. Genera, crea uno vacío o importa JSON."
        busy={busy}
        onSelect={(id) => {
          void openArtifact(id).catch((err: unknown) => {
            toast.error(err instanceof Error ? err.message : "No se pudo abrir");
          });
        }}
        onCreate={() => void onCreateEmpty()}
        onImport={(file) => void onImport(file)}
        onRename={async (item, title) => {
          await renameArtifact.mutateAsync({ artifactId: item.id, title });
        }}
        onDelete={async (item) => {
          await removeArtifact.mutateAsync(item.id);
          if (item.id === activeArtifactId) {
            const remaining = (artifacts ?? []).filter((entry) => entry.id !== item.id);
            if (remaining[0]) {
              await openArtifact(remaining[0].id);
            } else {
              setActiveArtifactId(null);
              setCards([]);
            }
          }
        }}
        onExport={(item) => void onExport(item)}
      />

      <div className="flex min-w-0 flex-1 flex-col overflow-y-auto pr-1">
        {readyDocs.length > 0 ? (
          <div className="mb-3">
            <DocumentScopePicker subjectId={subjectId} documents={readyDocs} />
          </div>
        ) : null}
        <FadeIn className="mb-4 flex w-full flex-col gap-3 sm:flex-row" y={6}>
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Concepto del temario (ej. BMC, cadena de valor)"
            disabled={readyDocs.length === 0}
          />
          <Button
            className="hover-lift"
            onClick={() => void onGenerate()}
            disabled={generating || readyDocs.length === 0}
          >
            {generating ? "Generando…" : "Generar"}
          </Button>
        </FadeIn>

        <Tabs value={mode} onValueChange={setMode} className="min-h-0 flex-1">
          <TabsList variant="line">
            <TabsTrigger value="practice">Practicar</TabsTrigger>
            <TabsTrigger value="edit" disabled={!activeArtifactId}>
              Editar
            </TabsTrigger>
          </TabsList>
          <TabsContent value="practice" className="pt-4">
            {!current ? (
              <EmptyState
                title="Sin deck todavía"
                description="Genera un conjunto, ábrelo en la biblioteca o crea tarjetas a mano."
              />
            ) : (
              <div className="mx-auto flex max-w-lg flex-col items-center gap-6">
                <p className="text-sm text-muted-foreground">
                  {index + 1} / {cards.length}
                </p>
                <div className="group/card perspective-1000 relative w-full">
                  <motion.button
                    type="button"
                    key={`${index}-${flipped}`}
                    onClick={() => setFlipped((v) => !v)}
                    className="relative min-h-52 w-full cursor-pointer rounded-lg border border-border bg-card px-8 py-12 text-center shadow-none outline-none transition-colors duration-200 group-hover/card:border-primary/50 group-hover/card:bg-accent/25 focus-visible:ring-2 focus-visible:ring-ring"
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
                  <p className="pointer-events-none mt-2 text-center text-[11px] text-muted-foreground opacity-0 transition-opacity duration-200 group-hover/card:opacity-100">
                    {flipped ? "Clic para ver el anverso" : "Clic para girar"}
                  </p>
                </div>
                {current.hint ? (
                  <div className="w-full max-w-lg text-center">
                    {hintOpen ? (
                      <p className="rounded-md border border-primary/20 bg-accent/40 px-3 py-2 text-sm text-accent-foreground">
                        {current.hint}
                      </p>
                    ) : (
                      <button
                        type="button"
                        className="cursor-pointer text-xs text-primary underline-offset-4 transition-colors hover:underline"
                        onClick={() => setHintOpen(true)}
                      >
                        Mostrar pista
                      </button>
                    )}
                  </div>
                ) : null}
                <p className="text-xs text-muted-foreground">
                  Space / Enter girar{current.hint ? " · H pista" : ""} · ← → navegar
                </p>
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
              </div>
            )}
          </TabsContent>
          <TabsContent value="edit" className="pt-4">
            {activeArtifactId ? (
              <FlashcardSetEditor
                cards={cards}
                busy={busy}
                onAdd={async (draft) => {
                  const created = await addCard.mutateAsync({ artifactId: activeArtifactId, ...draft });
                  setCards((curr) => [...curr, created]);
                }}
                onUpdate={async (cardId, draft) => {
                  const updated = await editCard.mutateAsync({
                    artifactId: activeArtifactId,
                    cardId,
                    ...draft,
                  });
                  setCards((curr) => curr.map((card) => (card.id === cardId ? updated : card)));
                }}
                onDelete={async (cardId) => {
                  await removeCard.mutateAsync({ artifactId: activeArtifactId, cardId });
                  setCards((curr) => curr.filter((card) => card.id !== cardId));
                  setIndex(0);
                  setFlipped(false);
                }}
              />
            ) : (
              <EmptyState title="Elige un deck" description="Abre un conjunto de la biblioteca para editarlo." />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
