"use client";

import Link from "next/link";

import { DeskScene } from "@/components/marketing/desk-scene";
import { FadeIn, Stagger, StaggerItem, motion } from "@/components/motion/fade-in";
import { Button } from "@/components/ui/button";

const LOOP = [
  {
    step: "01",
    title: "Documentos",
    copy: "Sube tus PDFs. Los indexamos página a página.",
  },
  {
    step: "02",
    title: "Entender",
    copy: "Pregunta en chat y recibe respuestas con citas.",
  },
  {
    step: "03",
    title: "Practicar",
    copy: "Flashcards y quiz generados desde tu material.",
  },
] as const;

export function LandingPage({ signedIn }: { signedIn: boolean }) {
  const primaryHref = signedIn ? "/subjects" : "/login";
  const primaryLabel = signedIn ? "Ir a mis asignaturas" : "Empezar";

  return (
    <div className="atmosphere grain relative min-h-dvh overflow-x-hidden">
      {/* —— Hero: one composition —— */}
      <section className="relative min-h-dvh">
        {/* Full-bleed visual plane */}
        <div className="pointer-events-none absolute inset-0 md:left-[38%]">
          <DeskScene className="h-full w-full opacity-90 md:opacity-100" />
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/85 to-transparent md:via-background/40 md:to-transparent" />
          <div className="absolute inset-x-0 bottom-0 h-40 bg-gradient-to-t from-background to-transparent md:hidden" />
        </div>

        <header className="relative z-20 flex items-center justify-between px-6 py-5 sm:px-10">
          <Link
            href="/"
            className="font-display text-lg font-bold tracking-tight transition-opacity hover:opacity-70"
          >
            Studyraft
          </Link>
          <Button asChild variant="ghost" className="hover-lift">
            <Link href={primaryHref}>{signedIn ? "Abrir app" : "Entrar"}</Link>
          </Button>
        </header>

        <div className="relative z-10 flex min-h-[calc(100dvh-4.5rem)] flex-col justify-center px-6 pb-24 pt-8 sm:px-10 md:max-w-[52%] lg:pb-32">
          <FadeIn y={16}>
            <h1 className="font-display text-[clamp(3.25rem,9vw,5.75rem)] font-bold leading-[0.95] tracking-tight text-foreground">
              Studyraft
            </h1>
          </FadeIn>

          <FadeIn delay={0.08} y={14}>
            <p className="mt-6 max-w-md text-lg leading-relaxed text-muted-foreground sm:text-xl">
              Convierte tus apuntes en un ciclo de estudio claro: indexa, pregunta y practica.
            </p>
          </FadeIn>

          <FadeIn delay={0.16} y={12} className="mt-10 flex flex-wrap items-center gap-3">
            <Button asChild size="lg" className="hover-lift px-8 text-base">
              <Link href={primaryHref}>{primaryLabel}</Link>
            </Button>
            {!signedIn ? (
              <Button asChild variant="outline" size="lg" className="hover-lift text-base">
                <Link href="/login?mode=signup">Crear cuenta</Link>
              </Button>
            ) : null}
          </FadeIn>

          <FadeIn delay={0.28} y={8} className="mt-14">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Tus PDFs · Tus respuestas · Tu ritmo
            </p>
          </FadeIn>
        </div>

        <motion.div
          className="pointer-events-none absolute bottom-8 left-1/2 z-10 hidden -translate-x-1/2 md:block"
          animate={{ y: [0, 6, 0] }}
          transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
          aria-hidden
        >
          <div className="h-8 w-px bg-gradient-to-b from-transparent via-primary/50 to-primary/20" />
        </motion.div>
      </section>

      {/* —— One job: the loop —— */}
      <section className="relative border-t border-border/70 bg-background/80 px-6 py-24 sm:px-10">
        <div className="mx-auto max-w-4xl">
          <FadeIn y={10}>
            <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
              Un ciclo. Sin ruido.
            </h2>
            <p className="mt-3 max-w-lg text-muted-foreground">
              Tres pasos. El mismo material. Sin paneles que distraigan.
            </p>
          </FadeIn>

          <Stagger className="mt-16 divide-y divide-border border-y border-border" delay={0.08}>
            {LOOP.map((item) => (
              <StaggerItem key={item.step}>
                <div className="group grid gap-3 py-8 transition-colors sm:grid-cols-[5rem_1fr] sm:items-baseline sm:gap-8">
                  <span className="font-display text-sm font-semibold text-primary transition-transform duration-200 group-hover:translate-x-0.5">
                    {item.step}
                  </span>
                  <div>
                    <h3 className="font-display text-xl font-semibold transition-colors group-hover:text-primary">
                      {item.title}
                    </h3>
                    <p className="mt-2 max-w-md text-muted-foreground">{item.copy}</p>
                  </div>
                </div>
              </StaggerItem>
            ))}
          </Stagger>

          <FadeIn delay={0.1} className="mt-14">
            <Button asChild size="lg" className="hover-lift">
              <Link href={primaryHref}>{primaryLabel}</Link>
            </Button>
          </FadeIn>
        </div>
      </section>

      <footer className="border-t border-border/60 px-6 py-8 sm:px-10">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-between gap-4 text-sm text-muted-foreground">
          <Link href="/" className="font-display font-semibold text-foreground transition-opacity hover:opacity-70">
            Studyraft
          </Link>
          <p>Estudio con tus propios documentos.</p>
        </div>
      </footer>
    </div>
  );
}
