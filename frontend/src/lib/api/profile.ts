import { apiRequest } from "@/lib/api/http";

export type ProfileDto = {
  id: string;
  email?: string | null;
  display_name?: string | null;
  avatar_url?: string | null;
  onboarding_completed: boolean;
  preferences: Record<string, unknown>;
};

export async function getProfile(token: string) {
  return apiRequest<ProfileDto>("/me", { token });
}

export async function updateProfile(
  token: string,
  body: { display_name?: string; preferences?: Record<string, unknown> },
) {
  return apiRequest<ProfileDto>("/me", { method: "PATCH", token, json: body });
}
