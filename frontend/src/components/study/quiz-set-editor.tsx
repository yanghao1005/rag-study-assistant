"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import type { QuizQuestionDto } from "@/lib/api/generation";

type Draft = {
  question: string;
  options: string[];
  correct_option_index: number;
  explanation: string;
};

const EMPTY_DRAFT: Draft = {
  question: "",
  options: ["", "", "", ""],
  correct_option_index: 0,
  explanation: "",
};

function toDraft(item: QuizQuestionDto): Draft {
  const options = [...item.options];
  while (options.length < 4) {
    options.push("");
  }
  return {
    question: item.question,
    options: options.slice(0, 4),
    correct_option_index: item.correct_option_index,
    explanation: item.explanation ?? "",
  };
}

export function QuizSetEditor({
  questions,
  busy,
  onAdd,
  onUpdate,
  onDelete,
}: {
  questions: QuizQuestionDto[];
  busy?: boolean;
  onAdd: (draft: {
    question: string;
    options: string[];
    correct_option_index: number;
    explanation?: string | null;
  }) => Promise<void>;
  onUpdate: (
    questionId: string,
    draft: {
      question: string;
      options: string[];
      correct_option_index: number;
      explanation?: string | null;
    },
  ) => Promise<void>;
  onDelete: (questionId: string) => Promise<void>;
}) {
  const [editingId, setEditingId] = useState<string | "new" | null>(null);
  const [draft, setDraft] = useState<Draft>(EMPTY_DRAFT);

  function payloadFromDraft() {
    const options = draft.options.map((opt) => opt.trim()).filter(Boolean);
    return {
      question: draft.question.trim(),
      options,
      correct_option_index: Math.min(draft.correct_option_index, Math.max(0, options.length - 1)),
      explanation: draft.explanation.trim() || null,
    };
  }

  async function save() {
    const payload = payloadFromDraft();
    if (!payload.question || payload.options.length < 2) {
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
        {questions.map((item, index) => (
          <li
            key={item.id ?? `${item.question}-${index}`}
            className="group rounded-md border border-border p-3 transition-colors duration-200 hover:border-primary/30 hover:bg-secondary/40"
          >
            {editingId === item.id ? (
              <QuestionForm
                draft={draft}
                busy={busy}
                onChange={setDraft}
                onCancel={() => setEditingId(null)}
                onSave={() => void save()}
              />
            ) : (
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <p className="text-sm font-medium">{item.question}</p>
                  <p className="mt-1 text-xs text-muted-foreground">{item.options.length} opciones</p>
                </div>
                <div className="flex shrink-0 gap-1 opacity-100 transition-opacity duration-150 [@media(hover:hover)]:opacity-0 [@media(hover:hover)]:group-hover:opacity-100 [@media(hover:hover)]:group-focus-within:opacity-100">
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={busy}
                    onClick={() => {
                      setEditingId(item.id ?? null);
                      setDraft(toDraft(item));
                    }}
                  >
                    Editar
                  </Button>
                  {item.id ? (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      disabled={busy}
                      onClick={() => void onDelete(item.id!)}
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
          <QuestionForm
            draft={draft}
            busy={busy}
            onChange={setDraft}
            onCancel={() => setEditingId(null)}
            onSave={() => void save()}
          />
        </div>
      ) : (
        <Button
          type="button"
          variant="outline"
          disabled={busy}
          onClick={() => {
            setEditingId("new");
            setDraft(EMPTY_DRAFT);
          }}
        >
          Añadir pregunta
        </Button>
      )}
    </div>
  );
}

function QuestionForm({
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
  const filled = draft.options.map((opt) => opt.trim()).filter(Boolean).length;
  return (
    <div className="flex flex-col gap-3">
      <div className="space-y-1">
        <Label htmlFor="quiz-question">Pregunta</Label>
        <Textarea
          id="quiz-question"
          value={draft.question}
          onChange={(event) => onChange({ ...draft, question: event.target.value })}
          rows={2}
        />
      </div>
      {draft.options.map((option, index) => (
        <div key={index} className="flex items-center gap-2">
          <input
            type="radio"
            name="correct-option"
            checked={draft.correct_option_index === index}
            onChange={() => onChange({ ...draft, correct_option_index: index })}
            aria-label={`Marcar opción ${index + 1} como correcta`}
          />
          <Input
            value={option}
            placeholder={`Opción ${index + 1}`}
            onChange={(event) => {
              const options = [...draft.options];
              options[index] = event.target.value;
              onChange({ ...draft, options });
            }}
          />
        </div>
      ))}
      <div className="space-y-1">
        <Label htmlFor="quiz-explanation">Explicación (opcional)</Label>
        <Textarea
          id="quiz-explanation"
          value={draft.explanation}
          onChange={(event) => onChange({ ...draft, explanation: event.target.value })}
          rows={2}
        />
      </div>
      <div className="flex gap-2">
        <Button type="button" disabled={busy || !draft.question.trim() || filled < 2} onClick={onSave}>
          Guardar
        </Button>
        <Button type="button" variant="outline" disabled={busy} onClick={onCancel}>
          Cancelar
        </Button>
      </div>
    </div>
  );
}
