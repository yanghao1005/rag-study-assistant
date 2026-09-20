"use client";

import Link from "next/link";
import { useState } from "react";

type Screen =
  | "login"
  | "subjects"
  | "documents"
  | "chat"
  | "flashcards"
  | "quiz";

const TABS: { id: Screen; label: string }[] = [
  { id: "login", label: "Login" },
  { id: "subjects", label: "Subjects" },
  { id: "documents", label: "Documents" },
  { id: "chat", label: "Chat" },
  { id: "flashcards", label: "Flashcards" },
  { id: "quiz", label: "Quiz" },
];

function ShellChrome({
  mode,
  children,
}: {
  mode: "documents" | "chat" | "flashcards" | "quiz";
  children: React.ReactNode;
}) {
  const modes = [
    { id: "documents", label: "Documentos" },
    { id: "chat", label: "Chat" },
    { id: "flashcards", label: "Flashcards" },
    { id: "quiz", label: "Quiz" },
  ] as const;

  return (
    <div className="flex min-h-[560px] overflow-hidden rounded-lg border border-border bg-background">
      <aside className="flex w-56 shrink-0 flex-col border-r border-border bg-background/80 p-4">
        <p className="font-display text-lg font-bold">Studyraft</p>
        <p className="mt-6 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Asignaturas
        </p>
        <nav className="mt-3 space-y-1">
          <div className="border-l-2 border-primary bg-accent/70 px-3 py-2 text-sm font-semibold text-accent-foreground">
            Biología celular
          </div>
          <div className="px-3 py-2 text-sm text-muted-foreground">Derecho mercantil</div>
        </nav>
        <button
          type="button"
          className="mt-3 px-3 py-2 text-left text-sm font-medium text-primary"
        >
          + Nueva
        </button>
        <div className="mt-auto border-t border-border pt-3 text-sm text-muted-foreground">
          Ajustes
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between gap-4 border-b border-border px-5 py-3">
          <div>
            <p className="font-display text-lg font-semibold">Biología celular</p>
            <div className="mt-2 flex gap-4">
              {modes.map((m) => (
                <span
                  key={m.id}
                  className={
                    m.id === mode
                      ? "border-b-2 border-primary pb-1 text-sm font-semibold text-foreground"
                      : "pb-1 text-sm text-muted-foreground"
                  }
                >
                  {m.label}
                </span>
              ))}
            </div>
          </div>
          <div className="size-8 rounded-full bg-secondary" aria-hidden />
        </header>
        <div className="flex-1 p-5">{children}</div>
      </div>
    </div>
  );
}

function LoginMock() {
  return (
    <div className="atmosphere relative flex min-h-[560px] items-center justify-center overflow-hidden rounded-lg border border-border">
      <div className="relative z-10 max-w-md px-6 text-center">
        <h2 className="font-display text-5xl font-bold tracking-tight">Studyraft</h2>
        <p className="mt-4 text-base leading-relaxed text-muted-foreground">
          Estudia con tus propios PDFs: indexa, pregunta con citas y practica.
        </p>
        <button
          type="button"
          className="mt-8 inline-flex h-11 w-full items-center justify-center rounded-md bg-primary text-sm font-semibold text-primary-foreground"
        >
          Continuar
        </button>
        <p className="mt-4 text-sm text-muted-foreground">¿No tienes cuenta? Crear una</p>
      </div>
    </div>
  );
}

function SubjectsMock() {
  return (
    <div className="min-h-[560px] rounded-lg border border-border bg-background p-8">
      <h2 className="font-display text-3xl font-bold">Tus asignaturas</h2>
      <p className="mt-2 max-w-lg text-muted-foreground">
        Elige qué estás estudiando. Todo lo demás (documentos, chat, práctica) vive dentro de una
        asignatura.
      </p>
      <ul className="mt-10 max-w-xl divide-y divide-border border-y border-border">
        <li className="flex items-center justify-between py-4">
          <div className="border-l-2 border-primary pl-3">
            <p className="font-semibold">Biología celular</p>
            <p className="text-sm text-muted-foreground">3 documentos · listos</p>
          </div>
          <span className="text-sm font-medium text-primary">Abrir</span>
        </li>
        <li className="flex items-center justify-between py-4 pl-3">
          <div>
            <p className="font-semibold">Derecho mercantil</p>
            <p className="text-sm text-muted-foreground">1 documento · procesando</p>
          </div>
          <span className="text-sm font-medium text-primary">Abrir</span>
        </li>
      </ul>
      <button
        type="button"
        className="mt-8 inline-flex h-11 items-center rounded-md bg-primary px-5 text-sm font-semibold text-primary-foreground"
      >
        Nueva asignatura
      </button>
    </div>
  );
}

function DocumentsMock() {
  return (
    <ShellChrome mode="documents">
      <div className="flex flex-col gap-6">
        <div className="rounded-md border border-dashed border-border px-6 py-12 text-center">
          <p className="font-display text-xl font-semibold">Sube un PDF</p>
          <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
            Arrastra el archivo aquí o elige desde tu equipo. Lo indexamos para chat y práctica.
          </p>
          <button
            type="button"
            className="mt-5 inline-flex h-10 items-center rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground"
          >
            Elegir archivo
          </button>
        </div>
        <ul className="divide-y divide-border border-y border-border">
          <li className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium">fotosintesis.pdf</p>
              <p className="text-sm text-muted-foreground">12 páginas · hace 2 min</p>
            </div>
            <span className="inline-flex items-center gap-2 text-sm">
              <span className="size-2 rounded-full bg-signal-ready" />
              Listo
            </span>
          </li>
          <li className="flex items-center justify-between py-3">
            <div>
              <p className="font-medium">mitocondrias.pdf</p>
              <p className="text-sm text-muted-foreground">Indexando… 55%</p>
            </div>
            <span className="inline-flex items-center gap-2 text-sm">
              <span className="size-2 animate-pulse rounded-full bg-signal-processing" />
              Procesando
            </span>
          </li>
        </ul>
      </div>
    </ShellChrome>
  );
}

function ChatMock() {
  return (
    <ShellChrome mode="chat">
      <div className="flex h-full min-h-[440px] flex-col">
        <div className="flex-1 space-y-6 overflow-auto">
          <div className="ml-auto max-w-md rounded-md bg-secondary px-4 py-3 text-sm">
            ¿Qué es el ciclo de Calvin según mis apuntes?
          </div>
          <div className="max-w-2xl space-y-3">
            <p className="text-[17px] leading-relaxed">
              El ciclo de Calvin fija dióxido de carbono en glucosa dentro del estroma del
              cloroplasto. Usa ATP y NADPH generados en la fase luminosa.[1]
            </p>
            <ol className="space-y-1 border-l-2 border-primary/40 pl-4 text-sm text-muted-foreground">
              <li>
                <button type="button" className="text-left hover:text-foreground">
                  [1] fotosintesis.pdf · pág. 5
                </button>
              </li>
            </ol>
          </div>
        </div>
        <div className="mt-4 flex gap-2 border-t border-border pt-4">
          <input
            readOnly
            value=""
            placeholder="Pregunta sobre esta asignatura…"
            className="h-11 flex-1 rounded-md border border-input bg-card px-3 text-sm"
          />
          <button
            type="button"
            className="h-11 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground"
          >
            Enviar
          </button>
        </div>
      </div>
    </ShellChrome>
  );
}

function FlashcardsMock() {
  return (
    <ShellChrome mode="flashcards">
      <div className="mx-auto flex max-w-lg flex-col items-center pt-4">
        <p className="text-sm text-muted-foreground">3 / 12 · Biología celular</p>
        <div className="mt-6 flex min-h-52 w-full items-center justify-center rounded-md border border-border bg-card px-8 py-12 text-center">
          <p className="text-lg leading-relaxed">
            ¿Qué longitudes de onda absorbe principalmente la clorofila?
          </p>
        </div>
        <p className="mt-3 text-xs text-muted-foreground">Space / Enter para girar</p>
        <div className="mt-8 flex gap-3">
          <button type="button" className="h-10 rounded-md border border-border px-4 text-sm font-medium">
            Anterior
          </button>
          <button
            type="button"
            className="h-10 rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground"
          >
            Girar
          </button>
          <button type="button" className="h-10 rounded-md border border-border px-4 text-sm font-medium">
            Siguiente
          </button>
        </div>
      </div>
    </ShellChrome>
  );
}

function QuizMock() {
  return (
    <ShellChrome mode="quiz">
      <div className="mx-auto max-w-xl">
        <p className="text-sm text-muted-foreground">Pregunta 2 de 8</p>
        <h3 className="mt-3 font-display text-2xl font-semibold leading-snug">
          ¿Dónde ocurre el ciclo de Calvin?
        </h3>
        <ul className="mt-8 space-y-3">
          {[
            "En la membrana tilacoidal",
            "En el estroma del cloroplasto",
            "En la matriz mitocondrial",
            "En el citoplasma",
          ].map((opt, i) => (
            <li key={opt}>
              <button
                type="button"
                className={`flex w-full items-center gap-3 rounded-md border px-4 py-3 text-left text-sm ${
                  i === 1
                    ? "border-primary bg-accent font-medium"
                    : "border-border hover:bg-secondary/60"
                }`}
              >
                <span className="text-muted-foreground">{i + 1}</span>
                {opt}
              </button>
            </li>
          ))}
        </ul>
        <button
          type="button"
          className="mt-8 h-11 rounded-md bg-primary px-5 text-sm font-semibold text-primary-foreground"
        >
          Confirmar
        </button>
      </div>
    </ShellChrome>
  );
}

export default function WireframesPage() {
  const [screen, setScreen] = useState<Screen>("login");

  return (
    <div className="atmosphere grain min-h-dvh">
      <div className="relative mx-auto max-w-6xl px-6 py-10 sm:px-8">
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-primary">Interface mockups · Nordic Desk</p>
            <h1 className="mt-1 font-display text-3xl font-bold">Cómo se ve Studyraft</h1>
            <p className="mt-2 max-w-xl text-muted-foreground">
              Prototipo visual (no funcional). Revisa cada pantalla antes de implementar Phase 6.
            </p>
          </div>
          <div className="flex gap-3 text-sm">
            <Link href="/design" className="font-medium text-foreground underline-offset-4 hover:underline">
              Tokens
            </Link>
            <Link href="/" className="font-medium text-muted-foreground underline-offset-4 hover:underline">
              Inicio
            </Link>
          </div>
        </div>

        <div className="mt-8 flex flex-wrap gap-2">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setScreen(tab.id)}
              className={
                screen === tab.id
                  ? "h-9 rounded-md bg-primary px-3 text-sm font-semibold text-primary-foreground"
                  : "h-9 rounded-md border border-border px-3 text-sm font-medium text-foreground hover:bg-accent"
              }
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="animate-enter mt-8">
          {screen === "login" ? <LoginMock /> : null}
          {screen === "subjects" ? <SubjectsMock /> : null}
          {screen === "documents" ? <DocumentsMock /> : null}
          {screen === "chat" ? <ChatMock /> : null}
          {screen === "flashcards" ? <FlashcardsMock /> : null}
          {screen === "quiz" ? <QuizMock /> : null}
        </div>

        <p className="mt-8 text-sm text-muted-foreground">
          Spec interactivo en el canvas del chat · fuente escrita en{" "}
          <code className="text-foreground">frontend/DESIGN.md</code>
        </p>
      </div>
    </div>
  );
}
