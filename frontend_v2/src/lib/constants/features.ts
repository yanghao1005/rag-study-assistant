export type FeatureKey =
  | "dashboard"
  | "subject"
  | "documents"
  | "generate"
  | "chat"
  | "history";

export type FeatureItem = {
  key: FeatureKey;
  title: string;
  href: string;
  description: string;
  enabled: boolean;
};

export const FEATURE_REGISTRY: FeatureItem[] = [
  {
    key: "dashboard",
    title: "Subjects",
    href: "/dashboard",
    description: "Subject directory and entry point.",
    enabled: true,
  },
  {
    key: "subject",
    title: "Subject Workspace",
    href: "/subject",
    description: "Feature launcher for the selected subject.",
    enabled: true,
  },
  {
    key: "documents",
    title: "Documents",
    href: "/documents/new",
    description: "Ingestion jobs and processed documents.",
    enabled: true,
  },
  {
    key: "generate",
    title: "Generate",
    href: "/generate",
    description: "Flashcards and quiz generation workspace.",
    enabled: true,
  },
  {
    key: "chat",
    title: "Chat",
    href: "/chat",
    description: "Grounded Q&A over document context.",
    enabled: true,
  },
  {
    key: "history",
    title: "History",
    href: "/history",
    description: "All generated study assets by scope.",
    enabled: true,
  },
];
