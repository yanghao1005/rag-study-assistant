"use client";

import { create } from "zustand";

const SUBJECT_KEY = "studyraft:v1:subjectId";

function normalizeId(value: string | null | undefined): string {
  const raw = (value || "").trim();
  if (!raw || ["undefined", "null", "nan"].includes(raw.toLowerCase())) {
    return "";
  }
  return raw;
}

export type SessionState = {
  hydrated: boolean;
  authResolved: boolean;
  token: string;
  userId: string;
  userEmail: string;
  subjectId: string;
  setAuthSession: (value: { token: string; userId: string; userEmail: string }) => void;
  setAuthResolved: (value: boolean) => void;
  setSubjectId: (value: string) => void;
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
  setAuthSession: (value) => {
    set({
      token: value.token,
      userId: value.userId,
      userEmail: value.userEmail,
      authResolved: true,
    });
  },
  setAuthResolved: (value) => set({ authResolved: value }),
  setSubjectId: (value) => {
    const normalized = normalizeId(value);
    if (typeof window !== "undefined") {
      if (normalized) {
        window.localStorage.setItem(SUBJECT_KEY, normalized);
      } else {
        window.localStorage.removeItem(SUBJECT_KEY);
      }
    }
    set({ subjectId: normalized });
  },
  clear: () => {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem(SUBJECT_KEY);
    }
    set({
      token: "",
      userId: "",
      userEmail: "",
      subjectId: "",
      authResolved: true,
    });
  },
  hydrate: () => {
    if (typeof window === "undefined") {
      return;
    }
    const subjectId = normalizeId(window.localStorage.getItem(SUBJECT_KEY));
    set({ hydrated: true, subjectId });
  },
}));
