"use client";

import {
  BookOpen,
  CalendarCheck,
  FileText,
  Layers3,
  LogOut,
  MessageSquareText,
  Plus,
  Settings,
  Sparkles,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTransition } from "react";
import { toast } from "sonner";

import { FadeIn } from "@/components/motion/fade-in";
import { CreateSubjectDialog } from "@/components/subjects/create-subject-dialog";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useSessionStore } from "@/features/auth/session-store";
import { useSubjects } from "@/features/subjects/use-subjects";
import { createClient } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";

const MODES = [
  { slug: "documents", label: "Documentos", icon: FileText },
  { slug: "chat", label: "Chat", icon: MessageSquareText },
  { slug: "flashcards", label: "Flashcards", icon: Layers3 },
  { slug: "quiz", label: "Quiz", icon: Sparkles },
  { slug: "planner", label: "Repaso", icon: CalendarCheck },
] as const;

export function AppShell({
  subjectId,
  children,
}: {
  subjectId?: string;
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { data: subjects, isLoading } = useSubjects();
  const setSubjectId = useSessionStore((s) => s.setSubjectId);
  const userEmail = useSessionStore((s) => s.userEmail);
  const clear = useSessionStore((s) => s.clear);
  const [pending, startTransition] = useTransition();

  const activeSubject = subjects?.find((s) => s.id === subjectId);
  const activeMode = MODES.find((m) => pathname.includes(`/${m.slug}`))?.slug ?? "documents";

  function signOut() {
    startTransition(async () => {
      const supabase = createClient();
      await supabase.auth.signOut();
      clear();
      router.replace("/login");
      router.refresh();
      toast.success("Sesión cerrada");
    });
  }

  return (
    <div className="flex min-h-dvh bg-background">
      <aside className="flex w-[var(--rail-width)] shrink-0 flex-col border-r border-border/80 bg-card/40 px-3 py-5 backdrop-blur-[2px]">
        <Link
          href="/subjects"
          className="group mx-1 flex items-center gap-2 font-display text-xl font-bold tracking-tight"
        >
          <span className="flex size-8 items-center justify-center rounded-md bg-primary text-primary-foreground transition-transform group-hover:scale-[1.03]">
            <BookOpen className="size-4" />
          </span>
          Studyraft
        </Link>

        <p className="mt-8 px-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Asignaturas
        </p>

        <ScrollArea className="mt-3 flex-1">
          <nav className="flex flex-col gap-1 pr-2">
            {isLoading ? (
              <>
                <Skeleton className="h-9 w-full" />
                <Skeleton className="h-9 w-full" />
              </>
            ) : null}
            {subjects?.map((subject) => (
              <Link
                key={subject.id}
                href={`/subjects/${subject.id}/documents`}
                onClick={() => setSubjectId(subject.id)}
                className={cn(
                  "cursor-pointer rounded-md px-3 py-2 text-sm transition-all duration-200",
                  subject.id === subjectId
                    ? "border-l-2 border-primary bg-accent font-semibold text-accent-foreground"
                    : "border-l-2 border-transparent text-muted-foreground hover:border-primary/40 hover:bg-secondary hover:text-foreground",
                )}
              >
                {subject.name}
              </Link>
            ))}
            <CreateSubjectDialog
              trigger={
                <Button
                  variant="ghost"
                  className="mt-1 justify-start gap-2 px-3 text-primary hover:text-primary"
                >
                  <Plus className="size-4" />
                  Nueva
                </Button>
              }
            />
          </nav>
        </ScrollArea>

        <Separator className="my-3" />
        <div className="flex flex-col gap-1 px-1">
          <p className="truncate px-2 text-xs text-muted-foreground">{userEmail}</p>
          <Link
            href="/settings"
            className={cn(
              "inline-flex cursor-pointer items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors duration-200",
              pathname.startsWith("/settings")
                ? "bg-accent font-semibold text-accent-foreground"
                : "text-muted-foreground hover:bg-secondary hover:text-foreground",
            )}
          >
            <Settings className="size-4" />
            Ajustes
          </Link>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size="sm"
                className="justify-start gap-2"
                disabled={pending}
                onClick={signOut}
              >
                <LogOut className="size-4" />
                Salir
              </Button>
            </TooltipTrigger>
            <TooltipContent>Cerrar sesión</TooltipContent>
          </Tooltip>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        {subjectId ? (
          <header className="border-b border-border/80 bg-background/80 px-6 py-4 backdrop-blur-sm">
            <FadeIn y={4}>
              <h1 className="truncate font-display text-xl font-semibold">
                {activeSubject?.name || "Asignatura"}
              </h1>
              <nav className="mt-3 flex flex-wrap gap-1">
                {MODES.map((mode) => {
                  const Icon = mode.icon;
                  const active = activeMode === mode.slug;
                  return (
                    <Link
                      key={mode.slug}
                      href={`/subjects/${subjectId}/${mode.slug}`}
                      className={cn(
                        "inline-flex cursor-pointer items-center gap-2 rounded-md px-3 py-2 text-sm transition-all duration-200",
                        active
                          ? "bg-accent font-semibold text-accent-foreground"
                          : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                      )}
                    >
                      <Icon className="size-4" />
                      {mode.label}
                    </Link>
                  );
                })}
              </nav>
            </FadeIn>
          </header>
        ) : null}
        <main className="flex-1 overflow-auto px-6 py-6">
          <FadeIn y={10}>{children}</FadeIn>
        </main>
      </div>
    </div>
  );
}
