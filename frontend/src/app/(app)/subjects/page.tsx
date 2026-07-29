"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { AppShell } from "@/components/shell/app-shell";
import { CreateSubjectDialog } from "@/components/subjects/create-subject-dialog";
import { FadeIn, Stagger, StaggerItem } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useSessionStore } from "@/features/auth/session-store";
import { useSubjects } from "@/features/subjects/use-subjects";

export default function SubjectsPage() {
  const router = useRouter();
  const { data: subjects, isLoading, isError, error } = useSubjects();
  const setSubjectId = useSessionStore((s) => s.setSubjectId);

  useEffect(() => {
    if (!isLoading && subjects && subjects.length === 0) {
      router.replace("/onboarding");
    }
  }, [isLoading, subjects, router]);

  return (
    <AppShell>
      {isLoading ? (
        <div className="mx-auto max-w-xl py-10">
          <Skeleton className="h-10 w-72" />
          <Skeleton className="mt-8 h-16 w-full" />
          <Skeleton className="mt-3 h-16 w-full" />
        </div>
      ) : null}

      {isError ? (
        <EmptyState
          title="No se pudieron cargar las asignaturas"
          description={
            error instanceof Error ? error.message : "Comprueba que el backend esté en marcha."
          }
        />
      ) : null}

      {!isLoading && !isError && subjects && subjects.length > 0 ? (
        <FadeIn className="mx-auto max-w-xl py-6" y={8}>
          <h1 className="font-display text-3xl font-bold">Tus asignaturas</h1>
          <p className="mt-2 text-muted-foreground">
            Elige qué estás estudiando. Documentos, chat y práctica viven dentro de cada
            asignatura.
          </p>

          <Stagger className="mt-10 divide-y divide-border border-y border-border" delay={0.06}>
            {subjects.map((subject) => (
              <StaggerItem key={subject.id}>
                <div className="flex items-center justify-between gap-4 py-4 transition-colors hover:bg-secondary/40">
                  <div className="min-w-0">
                    <p className="truncate font-semibold">{subject.name}</p>
                    {subject.description ? (
                      <p className="truncate text-sm text-muted-foreground">{subject.description}</p>
                    ) : null}
                  </div>
                  <Button asChild variant="ghost" className="text-primary">
                    <Link
                      href={`/subjects/${subject.id}/documents`}
                      onClick={() => setSubjectId(subject.id)}
                    >
                      Abrir
                    </Link>
                  </Button>
                </div>
              </StaggerItem>
            ))}
          </Stagger>

          <div className="mt-8">
            <CreateSubjectDialog trigger={<Button className="hover-lift">Nueva asignatura</Button>} />
          </div>
        </FadeIn>
      ) : null}
    </AppShell>
  );
}
