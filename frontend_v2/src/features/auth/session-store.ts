"use client";

import { create } from "zustand";

const SUBJECT_KEY = "frontend_v2_subject_id";
const DOC_KEY = "frontend_v2_document_id";
const INVALID_ID_VALUES = new Set(["undefined", "null", "nan"]);

function normalizeStoredId(value: string | null | undefined): string {
  const raw = (value || "").trim();
  if (!raw) {
    return "";
  }
  return INVALID_ID_VALUES.has(raw.toLowerCase()) ? "" : raw;
}

export type SessionState = {
  hydrated: boolean;
  authResolved: boolean;
  token: string;
  userId: string;
  userEmail: string;
  subjectId: string;
  documentId: string;
  setToken: (value: string) => void;
  setAuthResolved: (value: boolean) => void;
  setUser: (value: { userId: string; userEmail: string }) => void;
  setAuthSession: (value: { token: string; userId: string; userEmail: string }) => void;
  setSubjectId: (value: string) => void;
  setDocumentId: (value: string) => void;
  clear: () => void;
  hydrate: () => void;
};

export const useSessionStore = create<SessionState>((set) => ({
  hydrated: false,
  authResolved: false,
  token: "",
  userId: "",
  userEmail: "",
  subjectId: "",
  documentId: "",
  setToken: (value) => {
    set({ token: value });
  },
  setAuthResolved: (value) => {
    set({ authResolved: value });
  },
  setUser: (value) => {
    set({ userId: value.userId, userEmail: value.userEmail });
  },
  setAuthSession: (value) => {
    set({ token: value.token, userId: value.userId, userEmail: value.userEmail, authResolved: true });
  },
  setSubjectId: (value) => {
    const normalized = normalizeStoredId(value);
    if (typeof window !== "undefined") {
      if (normalized) {
        window.localStorage.setItem(SUBJECT_KEY, normalized);
      } else {
        window.localStorage.removeItem(SUBJECT_KEY);
      }
    }
    set({ subjectId: normalized });
  },
  setDocumentId: (value) => {
    const normalized = normalizeStoredId(value);
    if (typeof window !== "undefined") {
      if (normalized) {
        window.localStorage.setItem(DOC_KEY, normalized);
      } else {
        window.localStorage.removeItem(DOC_KEY);
      }
    }
    set({ documentId: normalized });
  },
  clear: () => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(SUBJECT_KEY);
      window.localStorage.removeItem(DOC_KEY);
    }
    set({ token: "", userId: "", userEmail: "", subjectId: "", documentId: "", authResolved: true });
  },
  hydrate: () => {
    if (typeof window === "undefined") {
      return;
    }

    const storedSubject = window.localStorage.getItem(SUBJECT_KEY);
    const storedDocument = window.localStorage.getItem(DOC_KEY);
    const subjectId = normalizeStoredId(storedSubject);
    const documentId = normalizeStoredId(storedDocument);

    if (storedSubject && !subjectId) {
      window.localStorage.removeItem(SUBJECT_KEY);
    }
    if (storedDocument && !documentId) {
      window.localStorage.removeItem(DOC_KEY);
    }

    set({
      hydrated: true,
      token: "",
      subjectId,
      documentId,
    });
  },
}));
