"use client";

import { useEffect, useRef } from "react";
import { Navbar } from "@/components/common/Navbar";
import { Sidebar } from "@/components/common/Sidebar";
import { useAuthStore } from "@/lib/store/authStore";
import { useSyncStore } from "@/lib/store/syncStore";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { initialize, user } = useAuthStore();
  const { initialize: initializeSync, syncNow } = useSyncStore();
  const lastSyncedUserIdRef = useRef<string | null>(null);

  useEffect(() => {
    initialize();
    initializeSync();
  }, [initialize, initializeSync]);

  useEffect(() => {
    if (user?.id && lastSyncedUserIdRef.current !== user.id) {
      lastSyncedUserIdRef.current = user.id;
      void syncNow(true);
    }
  }, [user?.id, syncNow]);

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-72 flex-col fixed inset-y-0 z-50">
        <Sidebar className="border-r" />
      </div>

      {/* Main Content */}
      <div className="flex-1 md:pl-72 flex flex-col min-h-screen">
        <Navbar />
        <main className="flex-1 container mx-auto px-4 py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
