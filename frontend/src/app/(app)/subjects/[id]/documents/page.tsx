"use client";

import { use } from "react";

import { DocumentsManager } from "@/components/documents/documents-manager";

export default function DocumentsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <DocumentsManager subjectId={id} />;
}
