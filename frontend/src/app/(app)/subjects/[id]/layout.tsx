"use client";

import { use, useEffect } from "react";

import { AppShell } from "@/components/shell/app-shell";
import { useSessionStore } from "@/features/auth/session-store";

export default function SubjectWorkspaceLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const setSubjectId = useSessionStore((s) => s.setSubjectId);

  useEffect(() => {
    setSubjectId(id);
  }, [id, setSubjectId]);

  return <AppShell subjectId={id}>{children}</AppShell>;
}
