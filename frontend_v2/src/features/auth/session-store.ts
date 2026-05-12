"use client";

import { create } from "zustand";

const SUBJECT_KEY = "frontend_v2_subject_id";
const DOC_KEY = "frontend_v2_document_id";

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
    if (typeof window !== "undefined") {
      window.localStorage.setItem(SUBJECT_KEY, value);
    }
    set({ subjectId: value });
  },
  setDocumentId: (value) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(DOC_KEY, value);
    }
    set({ documentId: value });
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

    set({
      hydrated: true,
      token: "",
      subjectId: window.localStorage.getItem(SUBJECT_KEY) || "",
      documentId: window.localStorage.getItem(DOC_KEY) || "",
    });
  },
}));
