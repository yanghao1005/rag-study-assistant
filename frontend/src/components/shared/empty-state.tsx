"use client";

import { FadeIn } from "@/components/motion/fade-in";

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <FadeIn className="mx-auto flex max-w-md flex-col items-center py-16 text-center" y={10}>
      <h2 className="font-display text-2xl font-semibold">{title}</h2>
      <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{description}</p>
      {action ? <div className="mt-6">{action}</div> : null}
    </FadeIn>
  );
}
