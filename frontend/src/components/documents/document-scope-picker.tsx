"use client";

import {
  useDocumentScopeStore,
  useSelectedDocumentIds,
} from "@/features/documents/use-document-scope";
import { cn } from "@/lib/utils";

type ReadyDocument = {
  id: string;
  filename: string;
};

export function DocumentScopePicker({
  subjectId,
  documents,
}: {
  subjectId: string;
  documents: ReadyDocument[];
}) {
  const selected = useSelectedDocumentIds(subjectId);
  const toggle = useDocumentScopeStore((s) => s.toggle);
  const clear = useDocumentScopeStore((s) => s.clear);
  const selectedSet = new Set(selected);

  if (documents.length === 0) {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          PDFs
        </p>
        {selected.length > 0 ? (
          <button
            type="button"
            className="cursor-pointer text-xs text-muted-foreground underline-offset-4 transition-colors duration-200 hover:text-foreground hover:underline"
            onClick={() => clear(subjectId)}
          >
            Usar todos
          </button>
        ) : (
          <span className="text-xs text-muted-foreground">
            Sin selección: busca en toda la asignatura
          </span>
        )}
      </div>
      <div className="flex flex-wrap gap-2">
        {documents.map((doc) => {
          const active = selectedSet.has(doc.id);
          return (
            <button
              key={doc.id}
              type="button"
              onClick={() => toggle(subjectId, doc.id)}
              aria-pressed={active}
              title={doc.filename}
              className={cn(
                "max-w-full cursor-pointer truncate rounded-full border px-3 py-1 text-xs transition-all duration-200 active:scale-[0.98]",
                active
                  ? "border-primary bg-accent font-medium text-accent-foreground"
                  : "border-border text-muted-foreground hover:border-primary/40 hover:bg-secondary hover:text-foreground",
              )}
            >
              {doc.filename}
            </button>
          );
        })}
      </div>
    </div>
  );
}
