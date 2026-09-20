"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn } from "@/components/motion/fade-in";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/lib/supabase/client";

export default function ResetPasswordPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [pending, startTransition] = useTransition();

  function submit(event: React.FormEvent) {
    event.preventDefault();
    if (password !== confirm) {
      toast.error("Las contraseñas no coinciden");
      return;
    }
    startTransition(async () => {
      const supabase = createClient();
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        toast.error(error.message);
        return;
      }
      toast.success("Contraseña actualizada");
      router.replace("/subjects");
      router.refresh();
    });
  }

  return (
    <main className="atmosphere grain relative flex min-h-dvh items-center justify-center px-6 py-16">
      <FadeIn className="soft-panel relative z-10 w-full max-w-md p-6" y={12}>
        <h1 className="font-display text-2xl font-semibold">Nueva contraseña</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Elige una contraseña nueva para tu cuenta Studyraft.
        </p>
        <form onSubmit={submit} className="mt-6 flex flex-col gap-4">
          <div className="flex flex-col gap-2">
            <Label htmlFor="password">Contraseña</Label>
            <Input
              id="password"
              type="password"
              required
              minLength={6}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="confirm">Confirmar</Label>
            <Input
              id="confirm"
              type="password"
              required
              minLength={6}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </div>
          <Button type="submit" className="hover-lift cursor-pointer" disabled={pending}>
            {pending ? "Guardando…" : "Guardar"}
          </Button>
          <Link href="/login" className="text-center text-sm text-muted-foreground hover:underline">
            Volver al login
          </Link>
        </form>
      </FadeIn>
    </main>
  );
}
