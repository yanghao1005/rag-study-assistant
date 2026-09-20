"use client";

import { useMutation } from "@tanstack/react-query";

import { uploadDocument } from "@/lib/api/backend";

export function useUploadDocument() {
  return useMutation({
    mutationFn: uploadDocument,
  });
}
