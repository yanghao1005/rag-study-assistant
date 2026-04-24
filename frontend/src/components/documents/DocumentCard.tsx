import { format } from 'date-fns';
import { FileText, StickyNote, Trash2, Eye, Download } from 'lucide-react';
import { Document } from '@/types/models';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { DocumentStatusBadge } from './DocumentStatusBadge';

interface DocumentCardProps {
  document: Document;
  onView: (id: string) => void;
  onDownload: (document: Document) => void;
  onDelete: (id: string) => void;
}

export function DocumentCard({ document, onView, onDownload, onDelete }: DocumentCardProps) {
  const isPdf = document.document_type === 'pdf';
  const Icon = isPdf ? FileText : StickyNote;

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <Card className="hover:shadow-sm transition-shadow">
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className={`p-2 rounded-lg ${isPdf ? 'bg-red-100 text-red-600' : 'bg-yellow-100 text-yellow-600'}`}>
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <h3 className="font-medium line-clamp-1 break-all" title={document.filename}>
                {document.filename}
              </h3>
              <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                <span>{format(new Date(document.created_at), 'MMM d, yyyy')}</span>
                <span>•</span>
                <span>{formatFileSize(document.file_size)}</span>
                {isPdf && document.total_pages && (
                  <>
                    <span>•</span>
                    <span>{document.total_pages} pages</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <DocumentStatusBadge status={document.status} />
        </div>
      </CardContent>
      <CardFooter className="p-2 bg-muted/20 flex justify-end gap-1">
        <Button variant="ghost" size="sm" onClick={() => onView(document.id)}>
          <Eye className="h-4 w-4 mr-2" />
          View
        </Button>
        <Button variant="ghost" size="sm" onClick={() => onDownload(document)}>
          <Download className="h-4 w-4 mr-2" />
          Download
        </Button>
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-destructive hover:text-destructive hover:bg-destructive/10"
          onClick={() => onDelete(document.id)}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
