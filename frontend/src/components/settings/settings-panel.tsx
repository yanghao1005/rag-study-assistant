"use client";

import { useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn } from "@/components/motion/fade-in";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useSessionStore } from "@/features/auth/session-store";
import { useProfile } from "@/features/profile/use-profile";
import { updateProfile } from "@/lib/api/profile";
import { useQueryClient } from "@tanstack/react-query";

export function SettingsPanel() {
  const token = useSessionStore((s) => s.token);
  const userEmail = useSessionStore((s) => s.userEmail);
  const { data: profile, isLoading } = useProfile();
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [agentic, setAgentic] = useState(false);
  const [hydrated, setHydrated] = useState(false);
  const [pending, startTransition] = useTransition();

  if (profile && !hydrated) {
    setName(profile.display_name || "");
    setAgentic(profile.preferences?.agentic_rag === true);
    setHydrated(true);
  }

  if (isLoading || !profile) {
    return (
      <div className="mx-auto max-w-lg space-y-3">
        <Skeleton className="h-10 w-48" />
        <Skeleton className="h-24 w-full" />
      </div>
    );
  }

  const currentProfile = profile;

  function save() {
    startTransition(async () => {
      try {
        await updateProfile(token, {
          display_name: name,
          preferences: { ...currentProfile.preferences, agentic_rag: agentic },
        });
        await queryClient.invalidateQueries({ queryKey: ["profile"] });
        toast.success("Ajustes guardados");
      } catch (err) {
        toast.error(err instanceof Error ? err.message : "No se pudo guardar");
      }
    });
  }

  return (
    <FadeIn className="mx-auto max-w-lg space-y-8" y={8}>
      <div>
        <h1 className="font-display text-3xl font-bold">Ajustes</h1>
        <p className="mt-2 text-sm text-muted-foreground">Tu perfil y preferencias de estudio.</p>
      </div>
      <div className="space-y-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" value={profile.email || userEmail} readOnly />
      </div>
      <div className="space-y-2">
        <Label htmlFor="display-name">Nombre</Label>
        <Input
          id="display-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Cómo te llamamos"
        />
      </div>
      <label className="flex items-start gap-3 text-sm">
        <input
          type="checkbox"
          className="mt-1 size-4"
          checked={agentic}
          onChange={(e) => setAgentic(e.target.checked)}
        />
        <span>
          <span className="font-medium">RAG agentic</span>
          <span className="mt-1 block text-muted-foreground">
            Si el contexto es flojo, reescribe la pregunta y busca otra vez (más lento, más
            preciso).
          </span>
        </span>
      </label>
      <Button className="hover-lift" onClick={save} disabled={pending}>
        {pending ? "Guardando…" : "Guardar"}
      </Button>
    </FadeIn>
  );
}
