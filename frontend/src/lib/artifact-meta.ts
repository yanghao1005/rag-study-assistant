import type { ArtifactOrigin, ArtifactSummaryDto } from "@/lib/api/generation";

const ORIGIN_LABEL: Record<ArtifactOrigin, string> = {
  generated: "IA",
  manual: "Manual",
  imported: "Importado",
};

export function artifactOriginLabel(origin?: string | null): string {
  if (origin === "manual" || origin === "imported" || origin === "generated") {
    return ORIGIN_LABEL[origin];
  }
  return ORIGIN_LABEL.generated;
}

export function formatArtifactDate(iso?: string | null): string {
  if (!iso) {
    return "";
  }
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return date.toLocaleString("es-ES", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function artifactLibraryMeta(
  item: ArtifactSummaryDto,
  itemNoun: string,
): string {
  const count = item.item_count ?? 0;
  const stamp = formatArtifactDate(item.updated_at || item.created_at);
  const parts = [`${count} ${itemNoun}`, stamp, artifactOriginLabel(item.origin)];
  return parts.filter(Boolean).join(" · ");
}

export function downloadJson(filename: string, data: unknown): void {
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function slugifyFilename(title: string): string {
  const slug = title
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 40);
  return slug || "set";
}
