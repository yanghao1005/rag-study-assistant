"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { citationLabel, type CitationDto } from "@/lib/citations";

export function CitationList({ citations }: { citations: CitationDto[] }) {
  const [open, setOpen] = useState<CitationDto | null>(null);

  if (citations.length === 0) {
    return null;
  }

  return (
    <>
      <ol className="space-y-1 border-l-2 border-primary/40 pl-4 text-sm">
        {citations.map((citation) => (
          <li key={`${citation.chunk_id}-${citation.index}`}>
            <button
              type="button"
              className="text-left text-muted-foreground underline-offset-4 transition-colors hover:text-foreground hover:underline"
              onClick={() => setOpen(citation)}
            >
              {citationLabel(citation)}
            </button>
          </li>
        ))}
      </ol>
      <Dialog open={Boolean(open)} onOpenChange={(next) => { if (!next) setOpen(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{open ? citationLabel(open) : "Cita"}</DialogTitle>
            <DialogDescription>
              {open?.chapter_name ? `Capítulo: ${open.chapter_name}` : "Fragmento del material indexado."}
            </DialogDescription>
          </DialogHeader>
          <p className="text-[17px] leading-relaxed whitespace-pre-wrap">
            {open?.snippet || "No hay extracto guardado para esta cita."}
          </p>
          <Button type="button" variant="outline" onClick={() => setOpen(null)}>
            Cerrar
          </Button>
        </DialogContent>
      </Dialog>
    </>
  );
}
