import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Defensa TFM",
  description: "Presentació de defensa de Studyraft, TFM d’Hao Yang.",
};

export default function PresentacioLayout({ children }: { children: React.ReactNode }) {
  return <>{children}</>;
}
