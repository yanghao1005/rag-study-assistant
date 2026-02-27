import { GeneratedHistoryItem } from "@/types/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { formatDistanceToNow } from "date-fns";
import { Clock, BookOpen, HelpCircle } from "lucide-react";

interface HistorySidebarProps {
  items: GeneratedHistoryItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  title?: string;
  description?: string;
  loading?: boolean;
  className?: string;
}

export function HistorySidebar({
  items,
  selectedId,
  onSelect,
  title = "History",
  description = "Select a generated item",
  loading = false,
  className,
}: HistorySidebarProps) {
  
  if (loading) {
    return (
      <Card className={cn("h-full border-none shadow-none bg-transparent lg:border lg:bg-card lg:shadow-sm", className)}>
        <CardHeader className="pb-3 px-4 pt-4">
          <Skeleton className="h-6 w-32 mb-2" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent className="px-2">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-16 w-full mb-2 rounded-lg" />
            ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("h-full border bg-card flex flex-col", className)}>
      <CardHeader className="pb-3 px-4 pt-4 shrink-0">
        <CardTitle className="text-lg">{title}</CardTitle>
        <CardDescription className="text-xs">{description}</CardDescription>
      </CardHeader>
      <CardContent className="px-2 grow overflow-hidden pb-2">
        <div className="h-full pr-3 overflow-y-auto">
          {items.length === 0 ? (
            <div className="text-center py-8 px-4 text-muted-foreground">
              <p className="text-sm">No items found.</p>
            </div>
          ) : (
            <div className="space-y-1">
              {items.map((item, index) => {
                const isSelected = selectedId === item.id;
                // Fallback title since API doesn't provide one directly yet
                const displayTitle = `${item.type === 'flashcard' ? 'Flashcards' : 'Quiz'} ${items.length - index}`;
                
                return (
                  <button
                    key={item.id}
                    onClick={() => onSelect(item.id)}
                    className={cn(
                      "w-full text-left flex flex-col gap-1 rounded-lg border p-3 text-sm transition-all hover:bg-accent",
                      isSelected
                        ? "bg-accent border-primary/50 shadow-sm"
                        : "border-transparent bg-transparent"
                    )}
                  >
                    <div className="flex w-full flex-col gap-1">
                      <div className="flex items-center gap-2">
                         {item.type === 'flashcard' ? <BookOpen className="h-3 w-3 text-primary" /> : <HelpCircle className="h-3 w-3 text-primary" />} 
                         <div className="font-semibold line-clamp-1">{displayTitle}</div>
                      </div>
                      <div className="flex items-center text-xs text-muted-foreground gap-2">
                        <Clock className="h-3 w-3" />
                        {item.created_at ? formatDistanceToNow(new Date(item.created_at), { addSuffix: true }) : "Unknown date"}
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
