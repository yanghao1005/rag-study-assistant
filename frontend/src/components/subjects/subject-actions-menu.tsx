"use client";

import { MoreHorizontal, Pencil, Trash2 } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { toast } from "sonner";

import { ConfirmDialog } from "@/components/shared/confirm-dialog";
import { SubjectEditDialog } from "@/components/subjects/subject-edit-dialog";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuGroup,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useSessionStore } from "@/features/auth/session-store";
import { useDeleteSubject, useSubjects } from "@/features/subjects/use-subjects";
import type { SubjectDto } from "@/lib/api/subjects";

export function SubjectActionsMenu({
  subject,
  className,
}: {
  subject: SubjectDto;
  className?: string;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { data: subjects } = useSubjects();
  const remove = useDeleteSubject();
  const currentSubjectId = useSessionStore((s) => s.subjectId);
  const setSubjectId = useSessionStore((s) => s.setSubjectId);

  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [pending, startTransition] = useTransition();

  function confirmDelete() {
    startTransition(async () => {
      try {
        await remove.mutateAsync(subject.id);
        const remaining = (subjects ?? []).filter((item) => item.id !== subject.id);
        const inWorkspace = pathname.startsWith(`/subjects/${subject.id}`);
        if (currentSubjectId === subject.id) {
          setSubjectId(remaining[0]?.id ?? "");
        }
        toast.success("Asignatura eliminada");
        setDeleteOpen(false);
        if (remaining.length === 0) {
          router.replace("/onboarding");
          return;
        }
        const nextSubject = remaining[0];
        if (inWorkspace && nextSubject) {
          router.replace(`/subjects/${nextSubject.id}/documents`);
        }
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "No se pudo eliminar");
      }
    });
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            className={className}
            aria-label={`Opciones de ${subject.name}`}
            onClick={(event) => event.stopPropagation()}
          >
            <MoreHorizontal />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" onClick={(event) => event.stopPropagation()}>
          <DropdownMenuGroup>
            <DropdownMenuItem onSelect={() => setEditOpen(true)}>
              <Pencil />
              Editar
            </DropdownMenuItem>
            <DropdownMenuItem variant="destructive" onSelect={() => setDeleteOpen(true)}>
              <Trash2 />
              Eliminar
            </DropdownMenuItem>
          </DropdownMenuGroup>
        </DropdownMenuContent>
      </DropdownMenu>

      <SubjectEditDialog subject={subject} open={editOpen} onOpenChange={setEditOpen} />
      <ConfirmDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        title={`¿Eliminar “${subject.name}”?`}
        description="Se borrarán sus documentos, chat y material de práctica. Esta acción no se puede deshacer."
        pending={pending || remove.isPending}
        onConfirm={confirmDelete}
      />
    </>
  );
}
