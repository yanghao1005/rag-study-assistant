import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, FileText, Activity, Zap } from "lucide-react";

interface DashboardStatsProps {
  totalSubjects: number;
  totalDocuments: number;
  isLoading: boolean;
}

export function DashboardStats({ totalSubjects, totalDocuments, isLoading }: DashboardStatsProps) {
    // Mock stats for now
    const studySessionsThisWeek = 12;
    const flashcardsReviewed = 145;

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Total Subjects
        </CardTitle>
        <BookOpen className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{totalSubjects}</div>
        <p className="text-xs text-muted-foreground">
          {isLoading ? "Loading..." : "Active learning paths"}
        </p>
      </CardContent>
    </Card>
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Knowledge Base
        </CardTitle>
        <FileText className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{totalDocuments}</div>
        <p className="text-xs text-muted-foreground">
          Documents uploaded
        </p>
      </CardContent>
    </Card>
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Study Sessions
        </CardTitle>
        <Activity className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{studySessionsThisWeek}</div>
        <p className="text-xs text-muted-foreground">
          +19% from last week
        </p>
      </CardContent>
    </Card>
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">
          Cards Reviewed
        </CardTitle>
        <Zap className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{flashcardsReviewed}</div>
        <p className="text-xs text-muted-foreground">
          Last 7 days
        </p>
      </CardContent>
    </Card>
  </div>
  );
}
