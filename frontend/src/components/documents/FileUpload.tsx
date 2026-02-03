import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, X, File as FileIcon, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface FileUploadProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  progress?: number;
  error?: string | null;
  maxSizeMB?: number; // default 10MB
  acceptedTypes?: Record<string, string[]>;
}

export function FileUpload({ 
  onFileSelect, 
  isUploading = false, 
  progress = 0,
  error = null,
  maxSizeMB = 10,
  acceptedTypes = { 'application/pdf': ['.pdf'] }
}: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: acceptedTypes,
    maxSize: maxSizeMB * 1024 * 1024,
    multiple: false,
    disabled: isUploading || !!selectedFile
  });

  const clearFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedFile(null);
    // Parent component needs to handle clearing their state too if needed
    // But usually we just submit after selecting
  };

  const errorMessage = error || (fileRejections.length > 0 
    ? fileRejections[0].errors[0].message 
    : null);

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={cn(
          "border-2 border-dashed rounded-xl p-8 transition-colors text-center cursor-pointer",
          isDragActive ? "border-primary bg-primary/5" : "border-muted-foreground/25",
          (isUploading || selectedFile) && "pointer-events-none opacity-80",
          errorMessage && "border-destructive/50 bg-destructive/5"
        )}
      >
        <input {...getInputProps()} />
        
        {selectedFile ? (
          <div className="flex flex-col items-center">
            <div className="bg-primary/10 p-4 rounded-full mb-4">
              <FileIcon className="h-8 w-8 text-primary" />
            </div>
            <p className="font-medium text-foreground">{selectedFile.name}</p>
            <p className="text-sm text-muted-foreground mb-2">
              {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
            </p>
            
            {!isUploading && (
               <Button 
                variant="ghost" 
                size="sm" 
                className="mt-2 text-destructive hover:text-destructive pointer-events-auto"
                onClick={clearFile}
               >
                 Change File
               </Button>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <div className="bg-muted p-4 rounded-full mb-4">
              <Upload className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-lg font-medium mb-1">
              {isDragActive ? "Drop file here" : "Drag & drop PDF here"}
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              or click to browse from your computer
            </p>
            <p className="text-xs text-muted-foreground">
              Maximum file size: {maxSizeMB}MB
            </p>
          </div>
        )}
      </div>

      {isUploading && (
        <div className="mt-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span>Uploading...</span>
            <span>{progress}%</span>
          </div>
          <Progress value={progress} />
        </div>
      )}

      {errorMessage && (
        <Alert variant="destructive" className="mt-4">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}
    </div>
  );
}
