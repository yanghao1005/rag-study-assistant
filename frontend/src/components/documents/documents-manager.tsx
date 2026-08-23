"use client";

import { useRef, useState, useTransition } from "react";
import { toast } from "sonner";

import { FadeIn, Stagger, StaggerItem } from "@/components/motion/fade-in";
import { EmptyState } from "@/components/shared/empty-state";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  useDeleteDocument,
  useJobStatus,
  useReindexDocument,
  useSubjectDocuments,
  useUploadDocument,
} from "@/features/documents/use-documents";
import { cn } from "@/lib/utils";

function StatusSignal({ status }: { status: string }) {
  const label =
    status === "ready"
      ? "Listo"
      : status === "processing"
        ? "Procesando"
        : status === "queued"
          ? "En cola"
          : status === "error"
            ? "Error"
            : status;

  return (
    <span className="inline-flex items-center gap-2 text-sm">
      <span
        className={cn(
          "size-2 rounded-full",
          status === "ready" && "bg-signal-ready",
          status === "processing" && "animate-pulse-soft bg-signal-processing",
          status === "queued" && "bg-muted-foreground/50",
          status === "error" && "bg-signal-error",
        )}
      />
      {label}
    </span>
  );
}

export function DocumentsManager({ subjectId }: { subjectId: string }) {
  const inputRef = useRef<HTMLInputElement>(null);
  const { data: documents, isLoading, isError, error, refetch } = useSubjectDocuments(subjectId);
  const upload = useUploadDocument(subjectId);
  const remove = useDeleteDocument(subjectId);
  const reindex = useReindexDocument(subjectId);
  const [activeJobId, setActiveJobId] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const job = useJobStatus(activeJobId, Boolean(activeJobId));

  async function onFiles(files: FileList | null) {
    if (!files?.length) {
      return;
    }
    const pdfs = [...files].filter((file) => file.name.toLowerCase().endsWith(".pdf"));
    if (pdfs.length === 0) {
      toast.error("Solo se admiten PDF por ahora.");
      return;
    }
    if (pdfs.length < files.length) {
      toast.error("Se ignoraron archivos que no son PDF.");
    }
    startTransition(async () => {
      const results = await Promise.allSettled(pdfs.map((file) => upload.mutateAsync(file)));
      const ok = results.filter((item) => item.status === "fulfilled");
      const fail = results.length - ok.length;
      if (ok.length === 1 && ok[0].status === "fulfilled") {
        setActiveJobId(ok[0].value.job_id);
        toast.success(`Subido: ${ok[0].value.filename}`);
      } else if (ok.length > 1) {
        const last = ok[ok.length - 1];
        if (last.status === "fulfilled") {
          setActiveJobId(last.value.job_id);
        }
        toast.success(`${ok.length} PDFs subidos`);
      }
      if (fail > 0) {
        toast.error(`${fail} archivo${fail === 1 ? "" : "s"} no se pudieron subir`);
      }
      await refetch();
    });
  }

  const progress =
    job.data?.status === "running" || job.data?.status === "queued"
      ? Number(job.data.progress || 0)
      : null;

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <FadeIn y={8}>
        <div
          className="soft-panel border-dashed px-6 py-12 text-center transition-colors hover:border-primary/40"
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            void onFiles(e.dataTransfer.files);
          }}
        >
          <p className="font-display text-xl font-semibold">Sube PDFs</p>
          <p className="mx-auto mt-2 max-w-sm text-sm text-muted-foreground">
            Arrastra uno o varios archivos aquí o elige desde tu equipo. Los indexamos para chat y
            práctica.
          </p>
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf,.pdf"
            multiple
            className="hidden"
            onChange={(e) => {
              void onFiles(e.target.files);
              e.target.value = "";
            }}
          />
          <Button
            className="mt-5 hover-lift"
            disabled={pending || upload.isPending}
            onClick={() => inputRef.current?.click()}
          >
            {pending || upload.isPending ? "Subiendo…" : "Elegir archivos"}
          </Button>
          {progress !== null ? (
            <div className="mx-auto mt-6 max-w-sm">
              <p className="mb-2 text-xs text-muted-foreground" aria-live="polite">
                Indexando… {Math.round(progress)}%
              </p>
              <Progress value={progress} />
            </div>
          ) : null}
        </div>
      </FadeIn>

      {isLoading ? (
        <div className="flex flex-col gap-3">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      ) : null}

      {isError ? (
        <EmptyState
          title="No se pudieron cargar los documentos"
          description={error instanceof Error ? error.message : "Error desconocido"}
        />
      ) : null}

      {!isLoading && !isError && documents && documents.length === 0 ? (
        <EmptyState
          title="Aún no hay documentos"
          description="Sube el primer PDF de esta asignatura para poder preguntar o practicar."
        />
      ) : null}

      {documents && documents.length > 0 ? (
        <Stagger className="divide-y divide-border border-y border-border" delay={0.05}>
          {documents.map((doc) => (
            <StaggerItem key={doc.id}>
              <div className="flex items-center justify-between gap-4 py-3 transition-colors hover:bg-secondary/40">
                <div className="min-w-0">
                  <p className="truncate font-medium">{doc.filename}</p>
                  <p className="text-sm text-muted-foreground">
                    {doc.total_pages ? `${doc.total_pages} páginas · ` : null}
                    {doc.error_message || `${Math.round((doc.file_size || 0) / 1024)} KB`}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <StatusSignal status={doc.status} />
                  {doc.status === "error" ? (
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={pending || reindex.isPending}
                      onClick={() => {
                        startTransition(async () => {
                          try {
                            const result = await reindex.mutateAsync(doc.id);
                            setActiveJobId(result.job_id);
                            toast.success("Reintentando indexación");
                            await refetch();
                          } catch (err) {
                            toast.error(
                              err instanceof Error ? err.message : "No se pudo reintentar",
                            );
                          }
                        });
                      }}
                    >
                      Reintentar
                    </Button>
                  ) : null}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive"
                    disabled={remove.isPending}
                    onClick={() => {
                      startTransition(async () => {
                        try {
                          await remove.mutateAsync(doc.id);
                          toast.success("Documento eliminado");
                        } catch (err) {
                          toast.error(err instanceof Error ? err.message : "No se pudo eliminar");
                        }
                      });
                    }}
                  >
                    Eliminar
                  </Button>
                </div>
              </div>
            </StaggerItem>
          ))}
        </Stagger>
      ) : null}
    </div>
  );
}
