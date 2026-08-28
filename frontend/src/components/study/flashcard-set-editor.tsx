"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { FlashcardDto } from "@/lib/api/generation";

type Draft = {
  front: string;
  back: string;
  hint: string;
};

const EMPTY_DRAFT: Draft = { front: "", back: "", hint: "" };

export function FlashcardSetEditor({
  cards,
  busy,
  onAdd,
  onUpdate,
  onDelete,
}: {
  cards: FlashcardDto[];
  busy?: boolean;
  onAdd: (draft: { front: string; back: string; hint?: string | null }) => Promise<void>;
  onUpdate: (
    cardId: string,
    draft: { front: string; back: string; hint?: string | null },
  ) => Promise<void>;
  onDelete: (cardId: string) => Promise<void>;
}) {
  const [editingId, setEditingId] = useState<string | "new" | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);

  function startEdit(card: FlashcardDto) {
    setEditingId(card.id ?? null);
    setDraft({ front: card.front, back: card.back, hint: card.hint ?? "" });
  }

  function startNew() {
    setEditingId("new");
    setDraft(EMPTY_DRAFT);
  }

  async function save() {
    const payload = {
      front: draft.front.trim(),
      back: draft.back.trim(),
      hint: draft.hint.trim() || null,
    };
    if (!payload.front || !payload.back) {
      return;
    }
    if (editingId && editingId !== "new") {
      await onUpdate(editingId, payload);
    } else {
      await onAdd(payload);
    }
    setEditingId(null);
    setDraft(EMPTY_DRAFT);
  }

  return (
    <div className="flex flex-col gap-4">
      <ul className="flex flex-col gap-2">
        {cards.map((card, index) => (
          <li
            key={card.id ?? `${card.front}-${index}`}
            className="group rounded-md border border-border p-3 transition-colors duration-200 hover:border-primary/30 hover:bg-secondary/40"
          >
            {editingId === card.id ? (
              <CardForm
                draft={draft}
                busy={busy}
                onChange={setDraft}
                onCancel={() => setEditingId(null)}
                onSave={() => void save()}
              />
            ) : (
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium">{card.front}</p>
                  <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{card.back}</p>
                  {card.hint ? (
                    <p className="mt-1 text-xs text-muted-foreground">Pista: {card.hint}</p>
                  ) : null}
                </div>
                <div className="flex shrink-0 gap-1 opacity-100 transition-opacity duration-150 [@media(hover:hover)]:opacity-0 [@media(hover:hover)]:group-hover:opacity-100 [@media(hover:hover)]:group-focus-within:opacity-100">
                  <Button type="button" variant="ghost" size="sm" disabled={busy} onClick={() => startEdit(card)}>
                    Editar
                  </Button>
                  {card.id ? (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      disabled={busy}
                      onClick={() => void onDelete(card.id!)}
                    >
                      Borrar
                    </Button>
                  ) : null}
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>

      {editingId === "new" ? (
        <div className="rounded-md border border-border p-3">
          <CardForm
            draft={draft}
            busy={busy}
            onChange={setDraft}
            onCancel={() => setEditingId(null)}
            onSave={() => void save()}
          />
        </div>
      ) : (
        <Button type="button" variant="outline" disabled={busy} onClick={startNew}>
          Añadir tarjeta
        </Button>
      )}
    </div>
  );
}

function CardForm({
  draft,
  busy,
  onChange,
  onCancel,
  onSave,
}: {
  draft: Draft;
  busy?: boolean;
  onChange: (draft: Draft) => void;
  onCancel: () => void;
  onSave: () => void;
}) {
  return (
    <div className="flex flex-col gap-3">
      <div className="space-y-1">
        <Label htmlFor="card-front">Anverso</Label>
        <Textarea
          id="card-front"
          value={draft.front}
          onChange={(event) => onChange({ ...draft, front: event.target.value })}
          rows={2}
        />
      </div>
      <div className="space-y-1">
        <Label htmlFor="card-back">Reverso</Label>
        <Textarea
          id="card-back"
          value={draft.back}
          onChange={(event) => onChange({ ...draft, back: event.target.value })}
          rows={3}
        />
      </div>
      <div className="space-y-1">
        <Label htmlFor="card-hint">Pista (opcional)</Label>
        <Input
          id="card-hint"
          value={draft.hint}
          onChange={(event) => onChange({ ...draft, hint: event.target.value })}
        />
      </div>
      <div className="flex gap-2">
        <Button type="button" disabled={busy || !draft.front.trim() || !draft.back.trim()} onClick={onSave}>
          Guardar
        </Button>
        <Button type="button" variant="outline" disabled={busy} onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    </div>
  );
}
