"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useTransition } from "react";
import { toast } from "sonner";

import { motion } from "@/components/motion/fade-in";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { createClient } from "@/lib/supabase/client";
import { cn } from "@/lib/utils";

type Mode = "signin" | "signup";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const next = searchParams.get("next") || "/subjects";
  const initialMode = searchParams.get("mode") === "signup" ? "signup" : "signin";

  const [mode, setMode] = useState<Mode>(initialMode);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [pending, startTransition] = useTransition();

  function submit(event: React.FormEvent) {
    event.preventDefault();
    startTransition(async () => {
      const supabase = createClient();
      const result =
        mode === "signin"
          ? await supabase.auth.signInWithPassword({ email, password })
          : await supabase.auth.signUp({ email, password });

      if (result.error) {
        toast.error(result.error.message);
        return;
      }

      if (mode === "signup" && !result.data.session) {
        toast.success("Revisa tu email para confirmar la cuenta.");
        return;
      }

      toast.success(mode === "signin" ? "Sesión iniciada" : "Cuenta creada");
      router.replace(next);
      router.refresh();
    });
  }

  return (
    <form onSubmit={submit} className="flex w-full flex-col gap-5">
      <div
        role="tablist"
        aria-label="Modo de acceso"
        className="relative grid grid-cols-2 rounded-md border border-border bg-secondary/40 p-1"
      >
        <motion.div
          className="absolute inset-y-1 w-[calc(50%-0.25rem)] rounded-sm bg-primary shadow-sm"
          initial={false}
          animate={{ left: mode === "signin" ? "0.25rem" : "calc(50% + 0.125rem)" }}
          transition={{ type: "spring", stiffness: 420, damping: 32 }}
          aria-hidden
        />
        {(
          [
            ["signin", "Entrar"],
            ["signup", "Crear cuenta"],
          ] as const
        ).map(([value, label]) => (
          <button
            key={value}
            type="button"
            role="tab"
            aria-selected={mode === value}
            className={cn(
              "relative z-10 cursor-pointer rounded-sm px-3 py-2 text-sm font-semibold transition-colors duration-200",
              mode === value
                ? "text-primary-foreground"
                : "text-muted-foreground hover:text-foreground",
            )}
            onClick={() => setMode(value)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="flex flex-col gap-2">
        <Label htmlFor="email" className="text-muted-foreground">
          Email
        </Label>
        <Input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="tu@email.com"
          className="h-11 bg-background/80 transition-[border-color,background-color,box-shadow] duration-200 hover:border-primary/35 hover:bg-background"
        />
      </div>

      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-2">
          <Label htmlFor="password" className="text-muted-foreground">
            Contraseña
          </Label>
          {mode === "signin" ? (
            <Link
              href="/forgot-password"
              className="text-xs text-primary underline-offset-4 hover:underline"
            >
              ¿Olvidaste la contraseña?
            </Link>
          ) : null}
        </div>
        <Input
          id="password"
          type="password"
          autoComplete={mode === "signin" ? "current-password" : "new-password"}
          required
          minLength={6}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Mínimo 6 caracteres"
          className="h-11 bg-background/80 transition-[border-color,background-color,box-shadow] duration-200 hover:border-primary/35 hover:bg-background"
        />
      </div>

      <Button
        type="submit"
        size="lg"
        disabled={pending}
        className="hover-lift h-11 w-full cursor-pointer text-base transition-transform duration-200 active:scale-[0.98]"
      >
        {pending ? "Espera…" : mode === "signin" ? "Continuar" : "Crear cuenta"}
      </Button>

      <p className="text-center text-sm text-muted-foreground">
        {mode === "signin" ? "¿Primera vez?" : "¿Ya tienes cuenta?"}{" "}
        <button
          type="button"
          className="cursor-pointer font-medium text-primary underline-offset-4 transition-colors hover:text-primary/80 hover:underline"
          onClick={() => setMode(mode === "signin" ? "signup" : "signin")}
        >
          {mode === "signin" ? "Crear cuenta" : "Entrar"}
        </button>
      </p>
    </form>
  );
}
