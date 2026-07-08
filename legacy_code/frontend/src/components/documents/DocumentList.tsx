import { Document } from '@/types/models';
import { DocumentCard } from './DocumentCard';
import { Skeleton } from '@/components/ui/skeleton';
import { FileText } from 'lucide-react';

interface DocumentListProps {
  documents: Document[];
  isLoading: boolean;
  onView: (id: string) => void;
  onDownload: (document: Document) => void;
  onDelete: (id: string) => void;
}

export function DocumentList({ documents, isLoading, onView, onDownload, onDelete }: DocumentListProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-24 w-full rounded-lg" />
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-12 border-2 border-dashed rounded-xl bg-muted/10">
        <div className="bg-muted w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="h-6 w-6 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-1">No documents found</h3>
        <p className="text-muted-foreground text-sm">
          Upload a PDF or create a summary to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-4">
      {documents.map((doc) => (
        <DocumentCard 
          key={doc.id} 
          document={doc} 
          onView={onView} 
          onDownload={onDownload}
          onDelete={onDelete} 
        />
      ))}
    </div>
  );
}
