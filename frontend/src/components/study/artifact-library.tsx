"use client";

import { useRef, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Skeleton } from "@/components/ui/skeleton";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { ArtifactSummaryDto } from "@/lib/api/generation";
import { artifactLibraryMeta } from "@/lib/artifact-meta";
import { cn } from "@/lib/utils";

type ArtifactLibraryProps = {
  items: ArtifactSummaryDto[] | undefined;
  loading?: boolean;
  activeId: string | null;
  itemNoun: string;
  createLabel: string;
  emptyLabel: string;
  busy?: boolean;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onImport: (file: File) => void;
  onRename: (item: ArtifactSummaryDto, title: string) => Promise<void>;
  onDelete: (item: ArtifactSummaryDto) => Promise<void>;
  onExport: (item: ArtifactSummaryDto) => void;
};

export function ArtifactLibrary({
  items,
  loading,
  activeId,
  itemNoun,
  createLabel,
  emptyLabel,
  busy,
  onSelect,
  onCreate,
  onImport,
  onRename,
  onDelete,
  onExport,
}: ArtifactLibraryProps) {
  const fileRef = useRef<HTMLInputElement>(null);
  const [renameItem, setRenameItem] = useState<ArtifactSummaryDto | null>(null);
  const [renameTitle, setRenameTitle] = useState("");
  const [deleteItem, setDeleteItem] = useState<ArtifactSummaryDto | null>(null);
  const list = items ?? [];

  async function confirmRename() {
    if (!renameItem) {
      return;
    }
    const title = renameTitle.trim();
    if (!title) {
      toast.error("El título no puede estar vacío.");
      return;
    }
    try {
      await onRename(renameItem, title);
      setRenameItem(null);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo renombrar");
    }
  }

  async function confirmDelete() {
    if (!deleteItem) {
      return;
    }
    try {
      await onDelete(deleteItem);
      setDeleteItem(null);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "No se pudo eliminar");
    }
  }

  return (
    <>
      <aside className="hidden w-56 shrink-0 flex-col border-r border-border pr-3 md:flex">
        <div className="mb-3 flex items-center justify-between gap-2">
          <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
            Biblioteca
          </p>
          <div className="flex items-center gap-0.5">
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-muted-foreground hover:text-foreground"
                  disabled={busy}
                  onClick={() => fileRef.current?.click()}
                >
                  Importar
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">Importar JSON</TooltipContent>
            </Tooltip>
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="h-7 px-2 text-primary hover:text-primary"
                  disabled={busy}
                  onClick={onCreate}
                >
                  {createLabel}
                </Button>
              </TooltipTrigger>
              <TooltipContent side="bottom">Crear conjunto vacío</TooltipContent>
            </Tooltip>
          </div>
        </div>
        <input
          ref={fileRef}
          type="file"
          accept="application/json,.json"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            event.target.value = "";
            if (file) {
              onImport(file);
            }
          }}
        />
        <ScrollArea className="flex-1">
          {loading ? <Skeleton className="h-16 w-full" /> : null}
          <ul className="space-y-0.5 pr-1">
            {list.map((item) => {
              const active = item.id === activeId;
              return (
                <li key={item.id} className="group relative flex items-stretch">
                  <button
                    type="button"
                    title={item.title || "Sin título"}
                    disabled={busy}
                    className={cn(
                      "min-w-0 flex-1 cursor-pointer rounded-md border-l-2 py-2 pr-8 pl-2 text-left text-sm transition-all duration-200",
                      "focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:outline-none",
                      active
                        ? "border-primary bg-accent font-medium text-accent-foreground hover:bg-accent/80"
                        : "border-transparent text-muted-foreground hover:border-primary/40 hover:bg-secondary hover:text-foreground",
                    )}
                    onClick={() => onSelect(item.id)}
                  >
                    <span className="line-clamp-2">{item.title || "Sin título"}</span>
                    <span
                      className={cn(
                        "mt-0.5 block text-[11px] font-normal transition-colors duration-200",
                        active ? "text-accent-foreground/70" : "text-muted-foreground group-hover:text-foreground/70",
                      )}
                    >
                      {artifactLibraryMeta(item, itemNoun)}
                    </span>
                  </button>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon-xs"
                        disabled={busy}
                        className={cn(
                          "absolute top-1.5 right-0.5 shrink-0 text-muted-foreground transition-opacity duration-150 hover:text-foreground",
                          "data-[state=open]:opacity-100",
                          active
                            ? "opacity-100"
                            : "opacity-100 [@media(hover:hover)]:opacity-0 [@media(hover:hover)]:group-hover:opacity-100 [@media(hover:hover)]:group-focus-within:opacity-100",
                        )}
                        aria-label={`Acciones de ${item.title}`}
                      >
                        ⋯
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => {
                          setRenameTitle(item.title);
                          setRenameItem(item);
                        }}
                      >
                        Renombrar
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => onExport(item)}>Exportar JSON</DropdownMenuItem>
                      <DropdownMenuItem variant="destructive" onClick={() => setDeleteItem(item)}>
                        Eliminar
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </li>
              );
            })}
          </ul>
          {!loading && list.length === 0 ? (
            <p className="px-1 text-xs text-muted-foreground">{emptyLabel}</p>
          ) : null}
        </ScrollArea>
      </aside>

      <div className="mb-3 md:hidden">
        <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-muted-foreground">
          Biblioteca
        </label>
        <select
          className="h-9 w-full cursor-pointer rounded-md border border-input bg-background px-3 text-sm transition-colors duration-200 hover:border-primary/40"
          value={activeId ?? ""}
          disabled={busy || list.length === 0}
          onChange={(event) => {
            if (event.target.value) {
              onSelect(event.target.value);
            }
          }}
        >
          {list.length === 0 ? <option value="">Sin conjuntos</option> : null}
          {list.map((item) => (
            <option key={item.id} value={item.id}>
              {item.title}
            </option>
          ))}
        </select>
        <div className="mt-2 flex gap-2">
          <Button type="button" variant="outline" size="sm" className="hover-lift" disabled={busy} onClick={onCreate}>
            {createLabel}
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="hover-lift"
            disabled={busy}
            onClick={() => fileRef.current?.click()}
          >
            Importar
          </Button>
        </div>
      </div>

      <Dialog open={Boolean(renameItem)} onOpenChange={(open) => !open && setRenameItem(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Renombrar conjunto</DialogTitle>
            <DialogDescription>El nombre aparece en la biblioteca, como el historial del chat.</DialogDescription>
          </DialogHeader>
          <Input
            value={renameTitle}
            onChange={(event) => setRenameTitle(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void confirmRename();
              }
            }}
            autoFocus
          />
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setRenameItem(null)}>
              Cancelar
            </Button>
            <Button type="button" onClick={() => void confirmRename()}>
              Guardar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={Boolean(deleteItem)} onOpenChange={(open) => !open && setDeleteItem(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Eliminar conjunto</DialogTitle>
            <DialogDescription>
              Se borrará «{deleteItem?.title}» y todo su contenido. Esta acción no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDeleteItem(null)}>
              Cancelar
            </Button>
            <Button type="button" variant="destructive" onClick={() => void confirmDelete()}>
              Eliminar
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
