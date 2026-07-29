"use client";

import { useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useSessionStore } from "@/features/auth/session-store";
import { createSubject } from "@/lib/api/subjects";

export function CreateSubjectDialog({
  trigger,
  onCreated,
}: {
  trigger: React.ReactNode;
  onCreated?: (subjectId: string) => void;
}) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const token = useSessionStore((s) => s.token);
  const setSubjectId = useSessionStore((s) => s.setSubjectId);

  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [pending, startTransition] = useTransition();

  function submit(event: React.FormEvent) {
    event.preventDefault();
    startTransition(async () => {
      try {
        const subject = await createSubject(token, {
          name: name.trim(),
          description: description.trim() || undefined,
        });
        await queryClient.invalidateQueries({ queryKey: ["subjects"] });
        setSubjectId(subject.id);
        setOpen(false);
        setName("");
        setDescription("");
        toast.success("Asignatura creada");
        onCreated?.(subject.id);
        router.push(`/subjects/${subject.id}/documents`);
      } catch (error) {
        toast.error(error instanceof Error ? error.message : "No se pudo crear");
      }
    });
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>{trigger}</DialogTrigger>
      <DialogContent>
        <form onSubmit={submit} className="flex flex-col gap-4">
          <DialogHeader>
            <DialogTitle>Nueva asignatura</DialogTitle>
            <DialogDescription>
              Todo tu material y estudio viven dentro de una asignatura.
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-2">
            <Label htmlFor="subject-name">Nombre</Label>
            <Input
              id="subject-name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Biología celular"
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="subject-desc">Descripción (opcional)</Label>
            <Textarea
              id="subject-desc"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Apuntes del cuatrimestre…"
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" disabled={pending || !name.trim()}>
              {pending ? "Creando…" : "Crear"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
