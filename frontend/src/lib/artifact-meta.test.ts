import { describe, expect, it } from "vitest";

import type { ArtifactSummaryDto } from "@/lib/api/generation";
import {
  artifactLibraryMeta,
  artifactOriginLabel,
  formatArtifactDate,
  slugifyFilename,
} from "@/lib/artifact-meta";

describe("artifact library meta", () => {
  it("labels origins and formats a row", () => {
    const item: ArtifactSummaryDto = {
      id: "1",
      artifact_type: "flashcard_deck",
      title: "BMC",
      status: "ready",
      subject_id: "s1",
      created_at: "2026-08-28T14:00:00.000Z",
      updated_at: "2026-08-28T16:30:00.000Z",
      item_count: 8,
      origin: "generated",
    };
    expect(artifactOriginLabel("manual")).toBe("Manual");
    expect(artifactLibraryMeta(item, "tarjetas")).toContain("8 tarjetas");
    expect(artifactLibraryMeta(item, "tarjetas")).toContain("IA");
    expect(artifactLibraryMeta(item, "tarjetas")).toContain(formatArtifactDate(item.updated_at));
    expect(artifactLibraryMeta(item, "tarjetas")).not.toContain(formatArtifactDate(item.created_at));
    expect(slugifyFilename("BMC y valor")).toBe("bmc-y-valor");
  });
});
