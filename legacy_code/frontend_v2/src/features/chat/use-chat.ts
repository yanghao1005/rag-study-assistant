"use client";

import { useMutation } from "@tanstack/react-query";

import { askChat } from "@/lib/api/backend";

export function useAskChat() {
  return useMutation({
    mutationFn: askChat,
  });
}
