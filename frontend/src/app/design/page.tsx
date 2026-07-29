import Link from "next/link";

const colors = [
  { name: "Background", swatch: "bg-background border border-border", hex: "mist paper" },
  { name: "Foreground", swatch: "bg-foreground", hex: "ink" },
  { name: "Primary", swatch: "bg-primary", hex: "teal" },
  { name: "Accent", swatch: "bg-accent border border-border", hex: "teal wash" },
  { name: "Muted", swatch: "bg-muted border border-border", hex: "cool gray" },
  { name: "Ready", swatch: "bg-signal-ready", hex: "signal" },
  { name: "Processing", swatch: "bg-signal-processing", hex: "signal" },
  { name: "Error", swatch: "bg-signal-error", hex: "signal" },
];

export default function DesignPage() {
  return (
    <div className="atmosphere grain min-h-dvh">
      <div className="relative mx-auto max-w-5xl px-6 py-16 sm:px-10">
        <header className="animate-enter max-w-2xl">
          <p className="text-sm font-medium tracking-wide text-primary">Design system · Nordic Desk</p>
          <h1 className="mt-3 font-display text-5xl font-bold tracking-tight text-foreground sm:text-6xl">
            Studyraft
          </h1>
          <p className="mt-4 max-w-xl text-lg leading-relaxed text-muted-foreground">
            Declaración visual y de interfaz para Phase 6–7. Un ciclo de estudio claro: asignatura →
            documentos → entender → practicar. Sin dashboard de IA genérico.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/"
              className="inline-flex h-11 items-center rounded-md bg-primary px-5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
            >
              Volver al inicio
            </Link>
          </div>
        </header>

        <section className="animate-enter mt-20" style={{ animationDelay: "60ms" }}>
          <h2 className="font-display text-2xl font-semibold">Color</h2>
          <p className="mt-2 text-muted-foreground">Un acento teal. Señales solo para estado de documento/job.</p>
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {colors.map((c) => (
              <div key={c.name} className="space-y-2">
                <div className={`h-20 rounded-md ${c.swatch}`} />
                <div>
                  <p className="text-sm font-semibold">{c.name}</p>
                  <p className="text-xs text-muted-foreground">{c.hex}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="animate-enter mt-20" style={{ animationDelay: "100ms" }}>
          <h2 className="font-display text-2xl font-semibold">Tipografía</h2>
          <div className="mt-6 space-y-6 border-t border-border pt-6">
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">Display · Syne</p>
              <p className="mt-2 font-display text-4xl font-bold">Estudiar con tus apuntes</p>
            </div>
            <div>
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Body · Source Sans 3
              </p>
              <p className="mt-2 max-w-2xl text-base leading-relaxed text-foreground">
                Las respuestas del chat deben leerse como material de estudio: cuerpo cómodo (16–18px),
                citas numeradas debajo, sin ruido visual. El usuario siempre sabe qué asignatura está
                activa.
              </p>
            </div>
          </div>
        </section>

        <section className="animate-enter mt-20" style={{ animationDelay: "140ms" }}>
          <h2 className="font-display text-2xl font-semibold">Componentes base</h2>
          <p className="mt-2 text-muted-foreground">Patrones, no un festival de cards.</p>

          <div className="mt-8 space-y-10">
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                className="inline-flex h-11 items-center rounded-md bg-primary px-5 text-sm font-semibold text-primary-foreground"
              >
                Acción primaria
              </button>
              <button
                type="button"
                className="inline-flex h-11 items-center rounded-md border border-border px-5 text-sm font-semibold"
              >
                Secundaria
              </button>
              <button
                type="button"
                className="inline-flex h-11 items-center rounded-md px-5 text-sm font-semibold text-destructive hover:bg-destructive/10"
              >
                Destructiva
              </button>
            </div>

            <div className="max-w-md space-y-2">
              <label htmlFor="demo-q" className="text-sm font-medium">
                Pregunta de estudio
              </label>
              <input
                id="demo-q"
                placeholder="¿Qué es el ciclo de Calvin?"
                className="h-11 w-full rounded-md border border-input bg-card px-3 text-sm placeholder:text-muted-foreground"
              />
            </div>

            <div className="border-y border-border py-4">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="font-medium">fotosintesis.pdf</p>
                  <p className="text-sm text-muted-foreground">12 páginas · hace 2 min</p>
                </div>
                <span className="inline-flex items-center gap-2 text-sm font-medium text-foreground">
                  <span className="size-2 rounded-full bg-signal-ready" aria-hidden />
                  Listo
                </span>
              </div>
            </div>

            <div className="rounded-md border border-dashed border-border px-6 py-12 text-center">
              <p className="font-display text-xl font-semibold">Aún no hay documentos</p>
              <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
                Sube un PDF de la asignatura para poder preguntar, generar flashcards o hacer un quiz.
              </p>
              <button
                type="button"
                className="mt-6 inline-flex h-11 items-center rounded-md bg-primary px-5 text-sm font-semibold text-primary-foreground"
              >
                Subir PDF
              </button>
            </div>

            <div className="mx-auto max-w-sm">
              <div className="flex min-h-48 items-center justify-center rounded-md border border-border bg-card px-6 py-10 text-center shadow-none">
                <p className="text-lg leading-relaxed">
                  La clorofila absorbe longitudes de onda azules y rojas.
                </p>
              </div>
              <p className="mt-3 text-center text-xs text-muted-foreground">
                Flashcard · Space para girar · ← → para navegar
              </p>
            </div>
          </div>
        </section>

        <section className="animate-enter mt-20 border-t border-border pt-10" style={{ animationDelay: "180ms" }}>
          <h2 className="font-display text-2xl font-semibold">Arquitectura de pantallas</h2>
          <ol className="mt-6 grid gap-4 sm:grid-cols-2">
            {[
              ["Subjects", "Elegir o crear la asignatura activa"],
              ["Documents", "Subir PDFs y ver estado de indexación"],
              ["Chat", "Preguntar al material con citas"],
              ["Flashcards / Quiz", "Practicar lo recuperado"],
            ].map(([title, desc], i) => (
              <li key={title} className="border-l-2 border-primary pl-4">
                <p className="text-xs font-semibold text-primary">{String(i + 1).padStart(2, "0")}</p>
                <p className="mt-1 font-semibold">{title}</p>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </li>
            ))}
          </ol>
        </section>

        <footer className="mt-24 text-sm text-muted-foreground">
          Fuente de verdad: <code className="text-foreground">frontend/DESIGN.md</code>
        </footer>
      </div>
    </div>
  );
}
