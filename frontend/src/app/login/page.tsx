import Link from "next/link";
import { Suspense } from "react";

import { LoginForm } from "@/components/auth/login-form";
import { DeskScene } from "@/components/marketing/desk-scene";
import { FadeIn } from "@/components/motion/fade-in";

export const metadata = {
  title: "Entrar",
};

export default function LoginPage() {
  return (
    <main className="atmosphere grain relative flex min-h-dvh overflow-hidden">
      {/* Subtle desk wash behind form */}
      <div className="pointer-events-none absolute inset-0 opacity-40 md:opacity-55">
        <DeskScene className="h-full w-full scale-110" />
        <div className="absolute inset-0 bg-gradient-to-b from-background/90 via-background/85 to-background" />
      </div>

      <div className="relative z-10 mx-auto flex w-full max-w-md flex-col justify-center px-6 py-16">
        <FadeIn y={14} className="text-center">
          <Link
            href="/"
            className="group inline-block font-display text-5xl font-bold tracking-tight transition-transform duration-300 hover:scale-[1.02] sm:text-6xl"
          >
            <span className="bg-gradient-to-br from-foreground to-foreground/75 bg-clip-text text-transparent transition-[filter] duration-300 group-hover:brightness-110">
              Studyraft
            </span>
          </Link>
          <p className="mx-auto mt-4 max-w-sm text-base leading-relaxed text-muted-foreground">
            Entra para indexar tus PDFs, preguntar con citas y practicar.
          </p>
        </FadeIn>

        <FadeIn className="mt-10" delay={0.1} y={16}>
          <div className="soft-panel border-border/70 p-5 shadow-[0_1px_0_oklch(1_0_0/0.4)_inset] transition-[border-color,box-shadow] duration-300 hover:border-primary/25 sm:p-6">
            <Suspense fallback={<div className="h-64 animate-pulse rounded-md bg-muted" />}>
              <LoginForm />
            </Suspense>
          </div>
        </FadeIn>

        <FadeIn delay={0.18} className="mt-6 text-center">
          <Link
            href="/"
            className="group inline-flex items-center gap-1 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <span className="transition-transform duration-200 group-hover:-translate-x-0.5">←</span>
            <span className="underline-offset-4 group-hover:underline">Volver al inicio</span>
          </Link>
        </FadeIn>
      </div>
    </main>
  );
}
