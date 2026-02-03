"use client";

import { useEffect } from "react";
import { Navbar } from "@/components/common/Navbar";
import { useAuthStore } from "@/lib/store/authStore";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { initialize } = useAuthStore();

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1 container mx-auto px-4 py-8">
        {children}
      </main>
    </div>
  );
}
