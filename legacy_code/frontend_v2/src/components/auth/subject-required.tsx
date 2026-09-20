"use client";

import Link from "next/link";
import { ArrowLeft } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useSessionStore } from "@/features/auth/session-store";

export function SubjectRequired({ children }: { children: React.ReactNode }) {
  const { subjectId } = useSessionStore();

  if (!subjectId) {
    return (
      <Card>
        <CardHeader>
          <Badge className="w-fit" variant="warning">
            Subject Required
          </Badge>
          <CardTitle>Select a subject first</CardTitle>
          <CardDescription>All study features are available inside a subject workspace.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild>
            <Link href="/dashboard">
              <ArrowLeft className="size-4" />
              Open Subjects Directory
            </Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  return <>{children}</>;
}
