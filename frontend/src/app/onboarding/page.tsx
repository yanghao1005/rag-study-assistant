"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { CreateSubjectDialog } from "@/components/subjects/create-subject-dialog";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useSubjects } from "@/features/subjects/use-subjects";

export default function OnboardingPage() {
  const router = useRouter();
  const { data: subjects, isLoading } = useSubjects();

  useEffect(() => {
    if (!isLoading && subjects && subjects.length > 0) {
      router.replace(`/subjects/${subjects[0].id}/documents`);
    }
  }, [isLoading, subjects, router]);

  if (isLoading) {
    return (
      <main className="mx-auto flex min-h-dvh max-w-lg flex-col justify-center px-6">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="mt-4 h-20 w-full" />
      </main>
    );
  }

  return (
    <main className="atmosphere grain flex min-h-dvh items-center justify-center px-6">
      <div className="animate-enter max-w-md text-center">
        <p className="font-display text-4xl font-bold">Studyraft</p>
        <h1 className="mt-6 font-display text-2xl font-semibold">Empieza con una asignatura</h1>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          Crea la primera asignatura. Después subirás un PDF y podrás preguntar o practicar.
        </p>
        <div className="mt-8">
          <CreateSubjectDialog trigger={<Button size="lg">Crear asignatura</Button>} />
        </div>
      </div>
    </main>
  );
}
