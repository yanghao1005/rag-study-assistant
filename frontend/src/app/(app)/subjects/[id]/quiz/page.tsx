"use client";

import { use } from "react";

import { QuizPanel } from "@/components/study/quiz-panel";

export default function QuizPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <QuizPanel subjectId={id} />;
}
