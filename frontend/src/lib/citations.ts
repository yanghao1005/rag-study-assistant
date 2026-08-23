export type CitationDto = {
  index: number;
  chunk_id: string;
  document_id: string;
  filename?: string | null;
  page_start?: number | null;
  page_end?: number | null;
  chapter_name?: string | null;
  snippet?: string | null;
  score?: number | null;
};

export function citationLabel(citation: CitationDto): string {
  const name = citation.filename?.trim() || `documento ${citation.document_id.slice(0, 8)}`;
  const page = citation.page_start != null ? ` · pág. ${citation.page_start}` : "";
  return `[${citation.index}] ${name}${page}`;
}
