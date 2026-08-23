import { PlannerPanel } from "@/components/study/planner-panel";

export default async function PlannerPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <PlannerPanel subjectId={id} />;
}
