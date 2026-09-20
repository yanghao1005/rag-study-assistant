"use client";

import { create } from "zustand";

const EMPTY_IDS: string[] = [];

type DocumentScopeState = {
  selectedBySubject: Record<string, string[]>;
  toggle: (subjectId: string, documentId: string) => void;
  clear: (subjectId: string) => void;
};

export const useDocumentScopeStore = create<DocumentScopeState>((set) => ({
  selectedBySubject: {},
  toggle: (subjectId, documentId) => {
    set((state) => {
      const current = state.selectedBySubject[subjectId] ?? [];
      const next = current.includes(documentId)
        ? current.filter((id) => id !== documentId)
        : [...current, documentId];
      return {
        selectedBySubject: { ...state.selectedBySubject, [subjectId]: next },
      };
    });
  },
  clear: (subjectId) => {
    set((state) => ({
      selectedBySubject: { ...state.selectedBySubject, [subjectId]: [] },
    }));
  },
}));

export function useSelectedDocumentIds(subjectId: string) {
  return useDocumentScopeStore((s) => s.selectedBySubject[subjectId] ?? EMPTY_IDS);
}

export function documentScopePayload(ids: string[]) {
  if (ids.length === 0) {
    return {};
  }
  return {
    document_ids: ids,
    document_id: ids.length === 1 ? ids[0] : undefined,
  };
}
