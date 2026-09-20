"use client";

import { useEffect, useMemo, useState, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useSyncStore } from "@/lib/store/syncStore";
import {
  clearQueuedMutations,
  getQueuedMutations,
  QueuedMutation,
  removeQueuedMutation,
} from "@/lib/offlineMutationQueue";
import { toast } from "sonner";
import { RefreshCw, Trash2, WifiOff, Wifi } from "lucide-react";

export default function SyncPage() {
  const { isOnline, isSyncing, lastSyncedAt, syncNow, refreshQueueCount } = useSyncStore();
  const [items, setItems] = useState<QueuedMutation[]>([]);

  const reload = useCallback(() => {
    setItems(getQueuedMutations());
    refreshQueueCount();
  }, [refreshQueueCount]);

  useEffect(() => {
    reload();
  }, [reload]);

  const grouped = useMemo(() => {
    const map = new Map<string, number>();
    for (const item of items) {
      map.set(item.type, (map.get(item.type) ?? 0) + 1);
    }
    return Array.from(map.entries());
  }, [items]);

  const handleReplay = async () => {
    try {
      await syncNow(true);
      reload();
      toast.success("Sync replay completed");
    } catch {
      toast.error("Failed to replay queue");
    }
  };

  const handleRemove = (id: string) => {
    removeQueuedMutation(id);
    reload();
    toast.success("Queued item removed");
  };

  const handleClear = () => {
    clearQueuedMutations();
    reload();
    toast.success("Queue cleared");
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Sync Queue</h1>
          <p className="text-muted-foreground mt-1">Manage offline actions pending backend replay.</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant={isOnline ? "default" : "secondary"} className="gap-1">
            {isOnline ? <Wifi className="h-3.5 w-3.5" /> : <WifiOff className="h-3.5 w-3.5" />}
            {isOnline ? "Online" : "Offline"}
          </Badge>
          <Button variant="outline" onClick={reload}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button onClick={handleReplay} disabled={isSyncing}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isSyncing ? "animate-spin" : ""}`} />
            {isSyncing ? "Syncing..." : "Replay Queue"}
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Queued Actions</CardDescription>
            <CardTitle>{items.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Last Sync</CardDescription>
            <CardTitle className="text-base">
              {lastSyncedAt ? new Date(lastSyncedAt).toLocaleString() : "Never"}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Status</CardDescription>
            <CardTitle className="text-base">{isSyncing ? "Syncing" : isOnline ? "Ready" : "Waiting online"}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Queue Summary</CardTitle>
          <CardDescription>Grouped by operation type.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-2">
          {grouped.length === 0 ? (
            <p className="text-sm text-muted-foreground">No queued operations.</p>
          ) : (
            grouped.map(([type, count]) => (
              <div key={type} className="flex items-center justify-between rounded-md border p-2 text-sm">
                <span>{type}</span>
                <Badge variant="secondary">{count}</Badge>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle>Queued Items</CardTitle>
            <CardDescription>Oldest first. Remove invalid ones manually if needed.</CardDescription>
          </div>
          <Button variant="destructive" size="sm" onClick={handleClear} disabled={items.length === 0}>
            <Trash2 className="h-4 w-4 mr-2" />
            Clear All
          </Button>
        </CardHeader>
        <CardContent className="space-y-3">
          {items.length === 0 ? (
            <p className="text-sm text-muted-foreground">Queue is empty.</p>
          ) : (
            items.map((item) => (
              <div key={item.id} className="rounded-md border p-3 flex items-start justify-between gap-4">
                <div className="space-y-1">
                  <p className="font-medium text-sm">{item.type}</p>
                  <p className="text-xs text-muted-foreground">Queued: {new Date(item.created_at).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground">Attempts: {item.attempts}</p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => handleRemove(item.id)}>
                  Remove
                </Button>
              </div>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
