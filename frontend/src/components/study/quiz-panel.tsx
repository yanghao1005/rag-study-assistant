"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { AnimatePresence, FadeIn, motion } from "@/components/motion/fade-in";
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
  useGenerateQuiz,
  useLoadArtifact,
} from "@/features/generation/use-generation";
import type { QuizQuestionDto } from "@/lib/api/generation";
import { cn } from "@/lib/utils";

export function QuizPanel({ subjectId }: { subjectId: string }) {
  const { data: documents, isLoading } = useSubjectDocuments(subjectId);
  const generate = useGenerateQuiz();
  const loadArtifact = useLoadArtifact();
  const { data: artifacts } = useArtifacts(subjectId, "quiz");
  const selectedDocumentIds = useSelectedDocumentIds(subjectId);
  const [questions, setQuestions] = useState<QuizQuestionDto[]>([]);
  const [index, setIndex] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [score, setScore] = useState(0);
  const [finished, setFinished] = useState(false);
  const [query, setQuery] = useState("");

  const readyDocs = documents?.filter((d) => d.status === "ready") ?? [];
  const current = questions[index];
  const generating = generate.isPending;

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (!current || finished) {
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
  }, [current, revealed, selected, index, questions.length, finished]);

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
      setQuestions(result.questions);
      setIndex(0);
      setSelected(null);
      setRevealed(false);
      setScore(0);
      setFinished(false);
      toast.success(`${result.questions.length} preguntas listas`);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Error al generar");
    }
  }

  async function onOpenArtifact(artifactId: string) {
    try {
      const artifact = await loadArtifact.mutateAsync(artifactId);
      if (!artifact.questions?.length) {
        toast.error("Este quiz no tiene preguntas.");
        return;
      }
      setQuestions(artifact.questions);
      setIndex(0);
      setSelected(null);
      setRevealed(false);
      setScore(0);
      setFinished(false);
      toast.success("Quiz cargado");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo cargar");
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

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (readyDocs.length === 0) {
    return (
      <EmptyState
        title="Necesitas documentos listos"
        description="Sube e indexa un PDF antes de generar un quiz."
      />
    );
  }

  return (
    <FadeIn className="mx-auto flex max-w-xl flex-col gap-6" y={8}>
      <DocumentScopePicker subjectId={subjectId} documents={readyDocs} />
      <div className="flex flex-col gap-3 sm:flex-row">
        <Input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Concepto del temario (ej. BMC)"
        />
        <Button className="hover-lift" onClick={() => void onGenerate()} disabled={generating}>
          {generating ? "Generando…" : "Generar quiz"}
        </Button>
      </div>

      {artifacts && artifacts.length > 0 ? (
        <div className="flex flex-wrap gap-2">
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
              {item.title || "Quiz"}
            </Button>
          ))}
        </div>
      ) : null}

      {finished ? (
        <EmptyState
          title={`Resultado: ${score} / ${questions.length}`}
          description="Puedes generar otro quiz o repetir este."
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
          description="Genera un quiz a partir de tus documentos indexados."
        />
      ) : (
        <AnimatePresence mode="wait">
          <motion.div
            key={index}
            initial={{ opacity: 0, x: 16 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -12 }}
            transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
            className="flex flex-col gap-6"
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
                        "flex w-full items-center gap-3 rounded-md border px-4 py-3 text-left text-sm transition-colors",
                        isSelected && !revealed && "border-primary bg-accent font-medium",
                        revealed && isCorrect && "border-signal-ready bg-signal-ready/10",
                        revealed && isSelected && !isCorrect && "border-signal-error bg-signal-error/10",
                        !isSelected && !revealed && "border-border hover:bg-secondary/60",
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
    </FadeIn>
  );
}
