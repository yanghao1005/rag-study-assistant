"use client";

import { useEffect, useState, useTransition } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useUpdateSubject } from "@/features/subjects/use-subjects";
import type { SubjectDto } from "@/lib/api/subjects";

export function SubjectEditDialog({
  subject,
  open,
  onOpenChange,
}: {
  subject: SubjectDto;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}) {
  const update = useUpdateSubject();
  const [name, setName] = useState(subject.name);
  const [description, setDescription] = useState(subject.description ?? "");
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    if (open) {
      setName(subject.name);
      setDescription(subject.description ?? "");
    }
  }, [open, subject.description, subject.name]);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    const trimmed = name.trim();
    if (!trimmed) {
      return;
    }
    startTransition(async () => {
      try {
        await update.mutateAsync({
          subjectId: subject.id,
          name: trimmed,
          description: description.trim() || null,
        });
        toast.success("Asignatura actualizada");
        onOpenChange(false);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "No se pudo guardar");
      }
    });
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <DialogHeader>
            <DialogTitle>Editar asignatura</DialogTitle>
            <DialogDescription>Cambia el nombre o la descripción.</DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-2">
            <Label htmlFor={`edit-subject-name-${subject.id}`}>Nombre</Label>
            <Input
              id={`edit-subject-name-${subject.id}`}
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor={`edit-subject-desc-${subject.id}`}>Descripción (opcional)</Label>
            <Textarea
              id={`edit-subject-desc-${subject.id}`}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={pending || !name.trim()}>
              {pending ? "Guardando…" : "Guardar"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
