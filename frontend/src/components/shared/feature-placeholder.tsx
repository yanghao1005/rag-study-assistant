import Link from "next/link";

import { EmptyState } from "@/components/shared/empty-state";

export function FeaturePlaceholder({
  title,
  description,
  ctaHref,
  ctaLabel,
}: {
  title: string;
  description: string;
  ctaHref?: string;
  ctaLabel?: string;
}) {
  return (
    <EmptyState
      title={title}
      description={description}
      action={
        ctaHref && ctaLabel ? (
          <Link
            href={ctaHref}
            className="inline-flex h-10 items-center rounded-md bg-primary px-4 text-sm font-semibold text-primary-foreground"
          >
            {ctaLabel}
          </Link>
        ) : undefined
      }
    />
  );
}
