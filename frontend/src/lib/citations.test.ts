import { describe, expect, it } from "vitest";

import { citationLabel, type CitationDto } from "@/lib/citations";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("merges tailwind classes", () => {
    expect(cn("px-2", "px-4")).toBe("px-4");
  });
});

describe("citationLabel", () => {
  it("uses filename and page", () => {
    const citation: CitationDto = {
      index: 1,
      chunk_id: "c1",
      document_id: "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
      filename: "bio.pdf",
      page_start: 4,
    };
    expect(citationLabel(citation)).toBe("[1] bio.pdf · pág. 4");
  });

  it("falls back to truncated id", () => {
    const citation: CitationDto = {
      index: 2,
      chunk_id: "c2",
      document_id: "abcd1234zzzz",
    };
    expect(citationLabel(citation)).toContain("[2] documento abcd1234");
  });
});
