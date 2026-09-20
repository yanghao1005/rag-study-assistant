"use client";

import { use } from "react";

import { FlashcardsPanel } from "@/components/study/flashcards-panel";

export default function FlashcardsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <FlashcardsPanel subjectId={id} />;
}
