"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { toast } from "sonner";

import { AnimatePresence, FadeIn, motion } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { DocumentScopePicker } from "@/components/documents/document-scope-picker";
import { ArtifactLibrary } from "@/components/study/artifact-library";
import { QuizSetEditor } from "@/components/study/quiz-set-editor";
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
  useAddQuizQuestion,
  useArtifacts,
  useCreateArtifact,
  useDeleteArtifact,
  useDeleteQuizQuestion,
  useGenerateQuiz,
  useLoadArtifact,
  useRenameArtifact,
  useUpdateQuizQuestion,
} from "@/features/generation/use-generation";
import type { ArtifactSummaryDto, QuizQuestionDto } from "@/lib/api/generation";
import { downloadJson, slugifyFilename } from "@/lib/artifact-meta";
import { cn } from "@/lib/utils";

export function QuizPanel({ subjectId }: { subjectId: string }) {
  const { data: documents, isLoading: docsLoading } = useSubjectDocuments(subjectId);
  const generate = useGenerateQuiz();
  const loadArtifact = useLoadArtifact();
  const { data: artifacts, isLoading: artifactsLoading } = useArtifacts(subjectId, "quiz");
  const createArtifact = useCreateArtifact();
  const renameArtifact = useRenameArtifact(subjectId);
  const removeArtifact = useDeleteArtifact(subjectId);
  const addQuestion = useAddQuizQuestion(subjectId);
  const editQuestion = useUpdateQuizQuestion(subjectId);
  const removeQuestion = useDeleteQuizQuestion(subjectId);
  const selectedDocumentIds = useSelectedDocumentIds(subjectId);
  const [questions, setQuestions] = useState<QuizQuestionDto[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("practice");
  const autoOpened = useRef(false);

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];
  const current = questions[index];
  const generating = generate.isPending;
  const busy =
    generating ||
    loadArtifact.isPending ||
    createArtifact.isPending ||
    renameArtifact.isPending ||
    removeArtifact.isPending ||
    addQuestion.isPending ||
    editQuestion.isPending ||
    removeQuestion.isPending;
  const hasLibrary = (artifacts?.length ?? 0) > 0;

  function resetPractice(next: QuizQuestionDto[]) {
    setQuestions(next);
    setIndex(0);
    setSelected(null);
    setRevealed(false);
    setScore(0);
    setFinished(false);
  }

  const openArtifact = useCallback(
    async (artifactId: string) => {
      const artifact = await loadArtifact.mutateAsync(artifactId);
      setActiveArtifactId(artifact.id);
      resetPractice(artifact.questions ?? []);
    },
    [loadArtifact],
  );

  useEffect(() => {
    autoOpened.current = false;
    setActiveArtifactId(null);
    resetPractice([]);
  }, [subjectId]);

  useEffect(() => {
    if (autoOpened.current || activeArtifactId || !artifacts?.length) {
      return;
    }
    autoOpened.current = true;
    void openArtifact(artifacts[0].id).catch((err: unknown) => {
      toast.error(err instanceof Error ? err.message : "No se pudo abrir el quiz");
    });
  }, [artifacts, activeArtifactId, openArtifact]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      if (target?.closest("input, textarea, select, [contenteditable='true']")) {
        return;
      }
      if (mode !== "practice" || !current || finished) {
        return;
      }
      if (e.key === "Enter") {
        e.preventDefault();
        if (!revealed && selected !== null) {
          confirmAnswer();
        } else if (revealed) {
          next();
        }
        return;
      }
      if (revealed) {
        return;
      }
      const num = Number(e.key);
      if (num >= 1 && num <= (current.options?.length || 0)) {
        setSelected(num - 1);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [current, revealed, selected, index, questions.length, finished, mode]);

  async function onGenerate() {
    try {
      const result = await generate.mutateAsync({
        subject_id: subjectId,
        count: 5,
        query: query.trim() || undefined,
        difficulty: "medium",
        ...documentScopePayload(selectedDocumentIds),
      });
      if (!result.questions.length) {
        toast.error("No se generaron preguntas.");
        return;
      }
      autoOpened.current = true;
      if (result.artifact_id) {
        await openArtifact(result.artifact_id);
      } else {
        resetPractice(result.questions);
      }
      setMode("practice");
      toast.success(`${result.questions.length} preguntas listas`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al generar");
    }
  }

  async function onCreateEmpty() {
    try {
      const created = await createArtifact.mutateAsync({
        subject_id: subjectId,
        artifact_type: "quiz",
        origin: "manual",
      });
      autoOpened.current = true;
      setActiveArtifactId(created.id);
      resetPractice([]);
      setMode("edit");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo crear el quiz");
    }
  }

  async function onImport(file: File) {
    try {
      const parsed = JSON.parse(await file.text()) as {
        title?: string;
        questions?: QuizQuestionDto[];
      };
      const imported = Array.isArray(parsed) ? parsed : parsed.questions;
      if (!Array.isArray(imported) || imported.length === 0) {
        toast.error("El JSON no contiene preguntas.");
        return;
      }
      const questionsPayload = imported
        .map((item) => ({
          question: String(item.question || "").trim(),
          options: Array.isArray(item.options) ? item.options.map(String) : [],
          correct_option_index: Number(item.correct_option_index) || 0,
          explanation: item.explanation ?? null,
        }))
        .filter((item) => item.question && item.options.length >= 2);
      if (!questionsPayload.length) {
        toast.error("El JSON no contiene preguntas válidas.");
        return;
      }
      const created = await createArtifact.mutateAsync({
        subject_id: subjectId,
        artifact_type: "quiz",
        title: typeof parsed.title === "string" ? parsed.title : file.name.replace(/\.json$/i, ""),
        origin: "imported",
        questions: questionsPayload,
      });
      autoOpened.current = true;
      await openArtifact(created.id);
      setMode("practice");
      toast.success(`Importadas ${questionsPayload.length} preguntas`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "JSON no válido");
    }
  }

  async function onExport(item: ArtifactSummaryDto) {
    try {
      const artifact =
        item.id === activeArtifactId
          ? { title: item.title, questions }
          : await loadArtifact.mutateAsync(item.id);
      downloadJson(`${slugifyFilename(artifact.title || item.title)}.json`, {
        title: artifact.title || item.title,
        questions: "questions" in artifact ? artifact.questions ?? questions : questions,
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo exportar");
    }
  }

  function confirmAnswer() {
    if (selected === null || !current) {
      return;
    }
    const correct = selected === current.correct_option_index;
    if (correct) {
      setScore((s) => s + 1);
    }
    setRevealed(true);
  }

  function next() {
    if (index >= questions.length - 1) {
      setFinished(true);
      return;
    }
    setIndex((i) => i + 1);
    setSelected(null);
    setRevealed(false);
  }

  if (docsLoading && artifactsLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (readyDocs.length === 0 && !hasLibrary && !artifactsLoading) {
    return (
      <EmptyState
        title="Necesitas documentos listos"
        description="Sube e indexa un PDF antes de generar un quiz, o importa un JSON."
      />
    );
  }

  return (
    <div className="mx-auto flex h-[calc(100dvh-11rem)] max-w-5xl flex-col gap-4 md:flex-row">
      <ArtifactLibrary
        items={artifacts}
        loading={artifactsLoading}
        activeId={activeArtifactId}
        itemNoun="preguntas"
        createLabel="Nuevo"
        emptyLabel="Aún no hay quizzes. Genera, crea uno vacío o importa JSON."
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
              resetPractice([]);
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
        <FadeIn className="mb-4 flex flex-col gap-3 sm:flex-row" y={8}>
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Concepto del temario (ej. BMC)"
            disabled={readyDocs.length === 0}
          />
          <Button
            className="hover-lift"
            onClick={() => void onGenerate()}
            disabled={generating || readyDocs.length === 0}
          >
            {generating ? "Generando…" : "Generar quiz"}
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
            {finished ? (
              <EmptyState
                title={`Resultado: ${score} / ${questions.length}`}
                description="Puedes generar otro quiz, repetir este o abrir otro de la biblioteca."
                action={
                  <Button
                    className="hover-lift"
                    onClick={() => {
                      setFinished(false);
                      setIndex(0);
                      setSelected(null);
                      setRevealed(false);
                      setScore(0);
                    }}
                  >
                    Repetir quiz
                  </Button>
                }
              />
            ) : !current ? (
              <EmptyState
                title="Sin preguntas todavía"
                description="Genera un quiz, ábrelo en la biblioteca o añade preguntas a mano."
              />
            ) : (
              <AnimatePresence mode="wait">
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 16 }}
                  animate={{ opacity: 1, y: 0, x: 0 }}
                  exit={{ opacity: 0, x: -12 }}
                  transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
                  className="flex max-w-xl flex-col gap-6"
                >
                  <p className="text-sm text-muted-foreground">
                    Pregunta {index + 1} de {questions.length}
                  </p>
                  <h2 className="font-display text-2xl font-semibold leading-snug">{current.question}</h2>
                  <ul className="flex flex-col gap-3">
                    {current.options.map((opt, i) => {
                      const isCorrect = i === current.correct_option_index;
                      const isSelected = selected === i;
                      return (
                        <li key={`${opt}-${i}`}>
                          <button
                            type="button"
                            disabled={revealed}
                            onClick={() => setSelected(i)}
                            className={cn(
                              "flex w-full cursor-pointer items-center gap-3 rounded-md border px-4 py-3 text-left text-sm transition-all duration-200",
                              "focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                              isSelected && !revealed && "border-primary bg-accent font-medium",
                              revealed && isCorrect && "border-signal-ready bg-signal-ready/10",
                              revealed && isSelected && !isCorrect && "border-signal-error bg-signal-error/10",
                              revealed && "cursor-default",
                              !isSelected && !revealed && "border-border hover:border-primary/40 hover:bg-secondary hover:text-foreground active:scale-[0.99]",
                            )}
                          >
                            <span className="text-muted-foreground">{i + 1}</span>
                            {opt}
                          </button>
                        </li>
                      );
                    })}
                  </ul>

                  {revealed && current.explanation ? (
                    <motion.p
                      initial={{ opacity: 0, y: 6 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-sm leading-relaxed text-muted-foreground"
                    >
                      {current.explanation}
                    </motion.p>
                  ) : null}

                  <div className="flex gap-3">
                    {!revealed ? (
                      <Button className="hover-lift" onClick={confirmAnswer} disabled={selected === null}>
                        Confirmar
                      </Button>
                    ) : (
                      <Button className="hover-lift" onClick={next}>
                        {index >= questions.length - 1 ? "Ver resultado" : "Siguiente"}
                      </Button>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">1–4 elige · Enter confirma o avanza</p>
                </motion.div>
              </AnimatePresence>
            )}
          </TabsContent>
          <TabsContent value="edit" className="pt-4">
            {activeArtifactId ? (
              <QuizSetEditor
                questions={questions}
                busy={busy}
                onAdd={async (draft) => {
                  const created = await addQuestion.mutateAsync({
                    artifactId: activeArtifactId,
                    ...draft,
                  });
                  setQuestions((curr) => [...curr, created]);
                }}
                onUpdate={async (questionId, draft) => {
                  const updated = await editQuestion.mutateAsync({
                    artifactId: activeArtifactId,
                    questionId,
                    ...draft,
                  });
                  setQuestions((curr) =>
                    curr.map((item) => (item.id === questionId ? updated : item)),
                  );
                }}
                onDelete={async (questionId) => {
                  await removeQuestion.mutateAsync({ artifactId: activeArtifactId, questionId });
                  setQuestions((curr) => curr.filter((item) => item.id !== questionId));
                  setIndex(0);
                  setSelected(null);
                  setRevealed(false);
                  setScore(0);
                  setFinished(false);
                }}
              />
            ) : (
              <EmptyState title="Elige un quiz" description="Abre un conjunto de la biblioteca para editarlo." />
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
