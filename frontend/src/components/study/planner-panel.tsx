"use client";

import { useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useDueCards, useReviewCard } from "@/features/planner/use-planner";

const RATINGS = [
  { quality: 1, label: "Otra vez" },
  { quality: 3, label: "Difícil" },
  { quality: 4, label: "Bien" },
  { quality: 5, label: "Fácil" },
] as const;

export function PlannerPanel({ subjectId }: { subjectId: string }) {
  const { data: due, isLoading, refetch } = useDueCards(subjectId);
  const review = useReviewCard(subjectId);
  const [flipped, setFlipped] = useState(false);
  const [pending, startTransition] = useTransition();

  const current = due?.[0];

  function rate(quality: number) {
    if (!current) {
      return;
    }
    startTransition(async () => {
      try {
        await review.mutateAsync({ flashcardId: current.flashcard_id, quality });
        setFlipped(false);
        await refetch();
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "No se pudo guardar el repaso");
      }
    });
  }

  if (isLoading) {
    return <Skeleton className="h-64 w-full" />;
  }

  if (!current) {
    return (
      <EmptyState
        title="Nada pendiente hoy"
        description="Cuando generes flashcards, aparecerán aquí según el intervalo de repaso."
      />
    );
  }

  return (
    <FadeIn className="mx-auto flex max-w-xl flex-col gap-6" y={8}>
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Repaso espaciado
        </p>
        <h1 className="mt-2 font-display text-2xl font-semibold">
          {due?.length} {(due?.length ?? 0) === 1 ? "tarjeta" : "tarjetas"} para hoy
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">{current.artifact_title}</p>
      </div>
      <button
        type="button"
        className="min-h-48 rounded-md border border-border bg-card px-6 py-10 text-left text-[18px] leading-relaxed"
        onClick={() => setFlipped((v) => !v)}
      >
        {flipped ? current.back : current.front}
      </button>
      <p className="text-xs text-muted-foreground">Clic para voltear · valora para programar</p>
      <div className="flex flex-wrap gap-2">
        {RATINGS.map((item) => (
          <Button
            key={item.quality}
            variant={item.quality === 1 ? "outline" : "secondary"}
            disabled={pending || review.isPending}
            onClick={() => rate(item.quality)}
          >
            {item.label}
          </Button>
        ))}
      </div>
    </FadeIn>
  );
}
