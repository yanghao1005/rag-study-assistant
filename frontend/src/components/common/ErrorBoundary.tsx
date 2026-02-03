import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { AlertCircle, RefreshCw } from "lucide-react";

interface ComponentErrorProps {
  error: Error | null;
  reset: () => void;
}

export function ErrorBoundaryComponent({ error, reset }: ComponentErrorProps) {
  return (
    <Alert variant="destructive" className="my-4">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>Something went wrong</AlertTitle>
      <AlertDescription className="mt-2 flex flex-col gap-2">
        <p>{error?.message || "An unexpected error occurred."}</p>
        <Button onClick={reset} variant="outline" size="sm" className="w-fit gap-2">
          <RefreshCw className="h-4 w-4" />
          Try Again
        </Button>
      </AlertDescription>
    </Alert>
  );
}
