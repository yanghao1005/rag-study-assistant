"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useSubjectStore } from "@/lib/store/subjectStore";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { BookOpen, FileText, BrainCircuit, Plus, ArrowRight, Activity, Zap } from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

export default function DashboardPage() {
  const { subjects, fetchSubjects, isLoading } = useSubjectStore();

  useEffect(() => {
    fetchSubjects();
  }, [fetchSubjects]);

  // Calculate stats
  const totalSubjects = subjects.length;
  const totalDocuments = subjects.reduce((acc, sub) => acc + (sub.document_count || 0), 0);
  
  // Mock stats
  const studySessionsThisWeek = 12;
  const flashcardsReviewed = 145;

  const recentSubjects = subjects.slice(0, 3);

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here&apos;s an overview of your learning progress.
        </p>
      </div>

      {/* Stats Grid */}
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

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Subjects */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Recent Subjects</CardTitle>
            <CardDescription>
              Continue where you left off.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
               <div className="space-y-4">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
               </div>
            ) : subjects.length > 0 ? (
               <div className="space-y-4">
                  {recentSubjects.map(subject => (
                    <div key={subject.id} className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors">
                       <div className="flex items-center gap-4">
                          <div className={`p-2 rounded-full bg-primary/10`}>
                             <BookOpen className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                             <h4 className="font-semibold">{subject.name}</h4>
                             <p className="text-sm text-muted-foreground">{subject.document_count || 0} documents</p>
                          </div>
                       </div>
                       <Button variant="ghost" size="sm" asChild>
                         <Link href={`/subjects/${subject.id}`}>
                           View
                           <ArrowRight className="ml-2 h-4 w-4" />
                         </Link>
                       </Button>
                    </div>
                  ))}
               </div>
            ) : (
                <div className="flex flex-col items-center justify-center py-8 text-center space-y-3">
                   <p className="text-muted-foreground">No subjects yet.</p>
                   <Button asChild variant="outline">
                      <Link href="/subjects">Create your first subject</Link>
                   </Button>
                </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="space-y-4">
            <Card className="bg-primary text-primary-foreground">
                <CardHeader>
                    <CardTitle>Start Studying</CardTitle>
                    <CardDescription className="text-primary-foreground/80">
                        Launch a new flashcard or quiz session.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Button variant="secondary" className="w-full" asChild>
                        <Link href="/study">
                           <BrainCircuit className="mr-2 h-4 w-4" />
                           Go to Study Mode
                        </Link>
                    </Button>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Quick Actions</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                    <Button variant="outline" className="w-full justify-start" asChild>
                        <Link href="/subjects">
                           <Plus className="mr-2 h-4 w-4" />
                           New Subject
                        </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                        <Link href="/study">
                           <Zap className="mr-2 h-4 w-4" />
                           Quick Review
                        </Link>
                    </Button>
                </CardContent>
            </Card>
        </div>
      </div>
    </div>
  );
}
