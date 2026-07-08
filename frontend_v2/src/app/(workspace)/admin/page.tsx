import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function AdminPage() {
  return (
    <Card className="mx-auto w-full max-w-5xl border-[var(--sl-muted)] bg-white shadow-sl-sm">
      <CardHeader>
        <Badge className="w-fit">Admin</Badge>
        <CardTitle>Admin Workspace (Reserved)</CardTitle>
        <CardDescription>This page is intentionally reserved for observability, cost, and quality controls.</CardDescription>
      </CardHeader>
      <CardContent className="text-sm text-muted-foreground">
        Placeholder enabled to preserve extension slots defined in `FINAL_SPEC.md`.
      </CardContent>
    </Card>
  );
}

