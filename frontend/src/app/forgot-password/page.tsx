"use client";

import Link from "next/link";
import { useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn } from "@/components/motion/fade-in";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/lib/supabase/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [pending, startTransition] = useTransition();
  const [sent, setSent] = useState(false);

  function submit(event: React.FormEvent) {
    event.preventDefault();
    startTransition(async () => {
      const supabase = createClient();
      const origin = window.location.origin;
      const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), {
        redirectTo: `${origin}/auth/callback?next=${encodeURIComponent("/reset-password")}`,
      });
      if (error) {
        toast.error(error.message);
        return;
      }
      setSent(true);
      toast.success("Te enviamos un enlace para restablecer la contraseña");
    });
  }

  return (
    <main className="atmosphere grain relative flex min-h-dvh items-center justify-center px-6 py-16">
      <FadeIn className="soft-panel relative z-10 w-full max-w-md p-6" y={12}>
        <h1 className="font-display text-2xl font-semibold">Recuperar contraseña</h1>
        <p className="mt-2 text-sm text-muted-foreground">
          Introduce tu email y te mandamos un enlace seguro.
        </p>
        {sent ? (
          <p className="mt-6 text-sm text-muted-foreground">
            Revisa tu bandeja de entrada (y spam).{" "}
            <Link href="/login" className="text-primary underline-offset-4 hover:underline">
              Volver a entrar
            </Link>
          </p>
        ) : (
          <form onSubmit={submit} className="mt-6 flex flex-col gap-4">
            <div className="flex flex-col gap-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@email.com"
              />
            </div>
            <Button type="submit" className="hover-lift cursor-pointer" disabled={pending}>
              {pending ? "Enviando…" : "Enviar enlace"}
            </Button>
            <Link href="/login" className="text-center text-sm text-muted-foreground hover:underline">
              Volver
            </Link>
          </form>
        )}
      </FadeIn>
    </main>
  );
}
