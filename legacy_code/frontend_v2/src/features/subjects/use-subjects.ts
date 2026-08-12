"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { getSupabaseBrowserClient } from "@/lib/supabase/client";

export type SubjectOption = {
  id: string;
  name: string;
};

export function useSubjects(enabled: boolean) {
  return useQuery({
    queryKey: ["subjects", "mine"],
    enabled,
    queryFn: async (): Promise<SubjectOption[]> => {
      const supabase = getSupabaseBrowserClient();
      const { data, error } = await supabase
        .from("subjects")
        .select("id,name")
        .order("created_at", { ascending: false })
        .limit(50);

      if (error) {
        throw new Error(error.message);
      }

      return (data || []).map((row) => ({
        id: String(row.id),
        name: String(row.name),
      }));
    },
  });
}

export function useCreateSubject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (name: string): Promise<SubjectOption> => {
      const normalizedName = name.trim();
      if (!normalizedName) {
        throw new Error("Subject name is required.");
      }

      const supabase = getSupabaseBrowserClient();
      const { data, error } = await supabase
        .from("subjects")
        .insert({
          name: normalizedName,
          description: null,
          color: null,
        })
        .select("id,name")
        .single();

      if (error) {
        throw new Error(error.message);
      }

      if (!data) {
        throw new Error("Failed to create subject.");
      }

      return {
        id: String(data.id),
        name: String(data.name),
      };
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["subjects", "mine"] });
    },
  });
}
