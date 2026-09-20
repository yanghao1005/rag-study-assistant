import { Document } from "@/types/models";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { FileText, StickyNote, Book } from "lucide-react";

interface SourceCitationProps {
  source: {
    document?: string;
    document_type: "pdf" | "summary";
    page?: number;
    chapter?: string;
  };
  compact?: boolean;
}

export function SourceCitation({ source, compact = false }: SourceCitationProps) {
  const isPdf = source.document_type === "pdf";
  const Icon = isPdf ? FileText : StickyNote;

  if (compact) {
    return (
      <Badge variant="outline" className="flex items-center gap-1 text-muted-foreground bg-muted/30">
        <Icon className="h-3 w-3" />
        <span className="truncate max-w-[150px]">{source.document}</span>
        {isPdf && source.page && <span>p. {source.page}</span>}
      </Badge>
    );
  }

  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground bg-secondary/30 p-2 rounded-md border border-secondary">
      <Icon className="h-4 w-4 text-primary" />
      <div className="flex flex-col">
        <span className="font-medium text-foreground">{source.document}</span>
        <div className="flex gap-2 text-xs">
          {source.chapter && <span>{source.chapter}</span>}
          {isPdf && source.page && <span>Page {source.page}</span>}
        </div>
      </div>
    </div>
  );
}
